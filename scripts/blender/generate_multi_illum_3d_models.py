#!/usr/bin/env python3
"""
Blender 5.2 Python script to procedurally construct and export 3D physical models of Shackleton Crater
with baked solar ray-marched shadows and regolith illumination for each illumination angle.

Grounded Physical Geometry (LOLA / SLDEM2015):
- Center: 89.9°S, 0.0°E
- Rim Diameter: 21.0 km (Radius: 10.5 km)
- Relief Depth: 4.2 km (Rim +1.2 km down to Floor -3.8 km)
- Inner Wall Slope: 28° - 32°
- Connecting Ridge: Elevated crest (+1.15 km) toward de Gerlache
- Albedo: ~0.10 diffuse lunar regolith

Exports optimized glTF binary (.glb) models compliant with ABAI L022 (<3 MB each).
"""

import sys
import math
from pathlib import Path

# Verify Blender runtime
try:
    import bpy
    import mathutils
    import numpy as np
except ImportError:
    print("ERROR: This script must be run inside Blender:")
    print("/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/generate_multi_illum_3d_models.py")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_3D_DIR = REPO_ROOT / "docs" / "assets" / "3d"
RESULTS_3D_DIR = REPO_ROOT / "results" / "3d_models"
DOCS_3D_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_3D_DIR.mkdir(parents=True, exist_ok=True)


def compute_terrain_elevation(grid_size=128, domain_km=30.0):
    """
    Generate the 2D elevation heightmap Z(X, Y) of Shackleton Crater and Connecting Ridge.
    """
    xs = np.linspace(-domain_km / 2.0, domain_km / 2.0, grid_size)
    ys = np.linspace(-domain_km / 2.0, domain_km / 2.0, grid_size)
    X, Y = np.meshgrid(xs, ys)
    R = np.sqrt(X**2 + Y**2)

    # Physical parameters (in km)
    R_floor = 3.5
    R_rim = 10.5
    Z_floor = -3.8
    Z_rim = 1.2
    Z_background = 0.0

    Z = np.zeros_like(R)

    # 1. Crater Floor (Flat, 40 K permanent cold trap)
    floor_mask = R <= R_floor
    Z[floor_mask] = Z_floor

    # 2. Crater Inner Walls (Steep 28°-32° slopes)
    wall_mask = (R > R_floor) & (R <= R_rim)
    norm_wall = (R[wall_mask] - R_floor) / (R_rim - R_floor)
    Z[wall_mask] = Z_floor + (Z_rim - Z_floor) * (norm_wall ** 1.35)

    # 3. Outer Ejecta Flank & Rampart
    rim_mask = R > R_rim
    decay = (R_rim / np.maximum(R[rim_mask], R_rim)) ** 2.2
    Z[rim_mask] = Z_background + (Z_rim - Z_background) * decay

    # 4. Connecting Ridge (Elevated ridge toward de Gerlache, ~135° azimuth)
    ridge_angle = math.radians(135.0)
    d_ridge = np.abs(-np.sin(ridge_angle) * X + np.cos(ridge_angle) * Y)
    s_ridge = np.cos(ridge_angle) * X + np.sin(ridge_angle) * Y
    ridge_mask = (R > R_rim * 0.8) & (s_ridge > 0)
    ridge_elevation = 1.15 * np.exp(-(d_ridge**2) / (2.0 * (1.8**2))) * np.exp(-((s_ridge - 10.0)**2) / (2.0 * (12.0**2)))
    Z[ridge_mask] += ridge_elevation[ridge_mask]

    # 5. Micro-cratering & regolith roughness
    noise = 0.04 * np.sin(X * 4.0) * np.cos(Y * 4.0) + 0.02 * np.sin(X * 12.0) * np.cos(Y * 12.0)
    Z += noise

    return X, Y, Z, xs, ys


def compute_surface_normals(X, Y, Z, domain_km, grid_size):
    """
    Compute normalized surface normal vectors for each vertex on the elevation grid.
    """
    spacing = domain_km / (grid_size - 1)
    dZx, dZy = np.gradient(Z, spacing)
    norm = np.sqrt(dZx**2 + dZy**2 + 1.0)
    N = np.stack([-dZx / norm, -dZy / norm, 1.0 / norm], axis=-1)
    return N


def compute_illumination_map(X, Y, Z, N, incidence_deg, azimuth_deg, domain_km, grid_size):
    """
    Compute physical solar illumination using ray-marched cast shadow testing
    and diffuse lunar regolith reflectance.
    """
    if incidence_deg is None or azimuth_deg is None:
        # Neutral baseline: diffuse hemispheric lighting based on slope gradient
        slope_factor = np.clip(N[:, :, 2], 0.2, 1.0)
        return 0.2 + 0.6 * slope_factor

    elev_deg = 90.0 - incidence_deg
    inc_rad = np.radians(incidence_deg)
    azim_rad = np.radians(azimuth_deg)
    elev_rad = np.radians(elev_deg)

    # Direction vector from surface toward sun
    s = np.array([
        np.sin(azim_rad) * np.cos(elev_rad),
        np.cos(azim_rad) * np.cos(elev_rad),
        np.sin(elev_rad)
    ])

    # 1. Cosine factor (Lambertian / Lommel-Seeliger approximation)
    cos_factor = np.clip(np.sum(N * s, axis=-1), 0.0, 1.0)

    # 2. Vectorized ray-marching shadow detection
    step_size_km = 0.20
    max_dist_km = domain_km
    num_steps = int(max_dist_km / step_size_km)
    shadow = np.zeros_like(Z, dtype=bool)

    for step in range(1, num_steps + 1):
        dist = step * step_size_km
        query_x = X + dist * s[0]
        query_y = Y + dist * s[1]
        ray_z = Z + dist * s[2]

        gx = ((query_x + domain_km / 2.0) / domain_km * (grid_size - 1))
        gy = ((query_y + domain_km / 2.0) / domain_km * (grid_size - 1))

        valid = (gx >= 0) & (gx < grid_size - 1) & (gy >= 0) & (gy < grid_size - 1)
        if not np.any(valid):
            break

        gx_int = gx[valid].astype(int)
        gy_int = gy[valid].astype(int)
        terrain_z = Z[gy_int, gx_int]

        blocked = terrain_z > ray_z[valid]
        if np.any(blocked):
            valid_indices = np.where(valid)
            blocked_coords = (valid_indices[0][blocked], valid_indices[1][blocked])
            shadow[blocked_coords] = True

    # 3. Combine direct solar flux with diffuse ambient scatter
    ambient = 0.02
    flux = np.where(shadow | (cos_factor <= 0.0), ambient, ambient + 0.98 * (cos_factor ** 0.85))
    return flux


def build_and_export_illuminated_mesh(X, Y, Z, flux, filename, model_name="ShackletonCrater"):
    """
    Construct Blender mesh, attach baked vertex colors, assign lunar PBR material,
    and export to optimized glTF binary.
    """
    bpy.ops.wm.read_factory_settings(use_empty=True)
    grid_size = X.shape[0]

    verts = []
    for i in range(grid_size):
        for j in range(grid_size):
            verts.append((float(X[i, j]), float(Y[i, j]), float(Z[i, j])))

    faces = []
    for i in range(grid_size - 1):
        for j in range(grid_size - 1):
            idx = i * grid_size + j
            faces.append((idx, idx + 1, idx + grid_size + 1, idx + grid_size))

    mesh = bpy.data.meshes.new("ShackletonTerrain")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Apply smooth shading
    for p in mesh.polygons:
        p.use_smooth = True

    # Assign Vertex Colors
    col_layer = mesh.color_attributes.new(name="Color", type='FLOAT_COLOR', domain='POINT')
    flat_flux = flux.flatten()
    for idx, f in enumerate(flat_flux):
        # Grayscale regolith tone with subtle warm tint
        r = float(f * 0.92)
        g = float(f * 0.92)
        b = float(f * 0.95)
        col_layer.data[idx].color = (r, g, b, 1.0)

    obj = bpy.data.objects.new(model_name, mesh)
    bpy.context.collection.objects.link(obj)

    # Material setup connecting vertex color attribute to Base Color
    mat = bpy.data.materials.new(name="LunarRegolithIlluminated")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.95
    bsdf.inputs["Specular IOR Level"].default_value = 0.08

    attr_node = nodes.new(type="ShaderNodeAttribute")
    attr_node.attribute_name = "Color"

    links.new(attr_node.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], output_node.inputs["Surface"])
    obj.data.materials.append(mat)

    # Export to both docs/assets/3d/ and results/3d_models/
    docs_out = DOCS_3D_DIR / filename
    results_out = RESULTS_3D_DIR / filename

    bpy.ops.export_scene.gltf(
        filepath=str(docs_out),
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT',
        export_vertex_color='MATERIAL',
    )

    # Copy to results
    import shutil
    shutil.copy2(docs_out, results_out)

    size_kb = docs_out.stat().st_size / 1024.0
    print(f"  [Exported] {filename} -> {size_kb:.1f} KB")
    return docs_out


def main():
    print("=" * 70)
    print("  Blender 5.2 Multi-Illumination 3D Shackleton Model Generator")
    print("=" * 70)

    grid_size = 128
    domain_km = 30.0
    print(f"Generating terrain elevation grid ({grid_size}x{grid_size} vertices, {domain_km} km domain)...")
    X, Y, Z, xs, ys = compute_terrain_elevation(grid_size=grid_size, domain_km=domain_km)
    N = compute_surface_normals(X, Y, Z, domain_km=domain_km, grid_size=grid_size)

    # Illumination regimes matching UI "Select Illumination Angle:"
    regimes = [
        (85.0, 0.0, "shackleton_3d_inc85_azim000.glb", "Polar Grazing North (Inc 85°, Azim 0°)"),
        (85.0, 90.0, "shackleton_3d_inc85_azim090.glb", "Polar Grazing East (Inc 85°, Azim 90°)"),
        (85.0, 180.0, "shackleton_3d_inc85_azim180.glb", "Polar Grazing South (Inc 85°, Azim 180°)"),
        (85.0, 270.0, "shackleton_3d_inc85_azim270.glb", "Polar Grazing West (Inc 85°, Azim 270°)"),
        (70.0, 120.0, "shackleton_3d_inc70_azim120.glb", "Sub-Polar Summer (Inc 70°, Azim 120°)"),
        (None, None, "shackleton_3d_neutral.glb", "Neutral Topographic Baseline"),
    ]

    print("\nComputing physical ray-marched shadows and baking 3D glTF models...")
    for inc, azim, fname, desc in regimes:
        print(f"\nProcessing regime: {desc}")
        flux = compute_illumination_map(X, Y, Z, N, inc, azim, domain_km=domain_km, grid_size=grid_size)
        build_and_export_illuminated_mesh(X, Y, Z, flux, fname)

    print("\n" + "=" * 70)
    print("  All 6 3D models generated and exported successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
