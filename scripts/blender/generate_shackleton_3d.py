#!/usr/bin/env python3
"""
Blender 5.2 Python script to build a schematic 3D model of a Shackleton-like crater and render
256 x 256 px tiles at a few illustrative lighting angles. The tiles are not LROC data and are
not run through the NASA-IBM Lunar Foundation Model.

Schematic geometry: an analytic bowl with a smooth ridge. It is NOT derived from LOLA or
SLDEM2015 data and has no geographic reference. Shackleton itself is centred at 89.67°S,
129.78°E with a 20.92 km diameter (IAU Gazetteer, feature 5450).
- Rim radius 10.5 km (21 km diameter), floor radius 3.5 km
- Rim +1.2 km, floor -3.8 km: 5.0 km relief in the model (a modelling choice, not a measurement)
- A smooth ridge (+1.15 km) added at 135° azimuth to suggest the Shackleton-de Gerlache ridge
"""

import sys
import math
from pathlib import Path

# Check that script is running inside Blender
try:
    import bpy
    import mathutils
    import numpy as np
except ImportError:
    print("ERROR: This script must be run inside Blender:")
    print("/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/blender/generate_shackleton_3d.py")
    sys.exit(1)

# Repository paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = REPO_ROOT / "results" / "blender_renders"
DOCS_ASSETS_DIR = REPO_ROOT / "docs" / "assets"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def clear_scene():
    """Remove all objects, meshes, cameras, and lights from the scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build_shackleton_mesh(grid_size=160, domain_km=30.0):
    """
    Construct 3D surface mesh of Shackleton Crater and Connecting Ridge.
    
    Dimensions:
    - Domain: 30 km x 30 km
    - Resolution: grid_size x grid_size vertices
    """
    print(f"Constructing Shackleton 3D mesh ({grid_size}x{grid_size} grid, {domain_km} km domain)...")
    xs = np.linspace(-domain_km / 2.0, domain_km / 2.0, grid_size)
    ys = np.linspace(-domain_km / 2.0, domain_km / 2.0, grid_size)
    X, Y = np.meshgrid(xs, ys)
    R = np.sqrt(X**2 + Y**2)
    theta = np.arctan2(Y, X)

    # Schematic geometry parameters (in km)
    R_floor = 3.5
    R_rim = 10.5
    Z_floor = -3.8
    Z_rim = 1.2
    Z_background = 0.0

    Z = np.zeros_like(R)

    # 1. Crater floor (flat)
    floor_mask = R <= R_floor
    Z[floor_mask] = Z_floor

    # 2. Crater inner walls (power-law profile)
    wall_mask = (R > R_floor) & (R <= R_rim)
    norm_wall = (R[wall_mask] - R_floor) / (R_rim - R_floor)
    Z[wall_mask] = Z_floor + (Z_rim - Z_floor) * (norm_wall ** 1.35)

    # 3. Outer Ejecta Flank & Rampart
    rim_mask = R > R_rim
    decay = (R_rim / np.maximum(R[rim_mask], R_rim)) ** 2.2
    Z[rim_mask] = Z_background + (Z_rim - Z_background) * decay

    # 4. Schematic ridge at ~135° azimuth (suggests the Shackleton-de Gerlache ridge; not real terrain)
    ridge_angle = math.radians(135.0)
    # Perpendicular distance to ridge centerline
    d_ridge = np.abs(-np.sin(ridge_angle) * X + np.cos(ridge_angle) * Y)
    # Along ridge distance (positive in northwest direction)
    s_ridge = np.cos(ridge_angle) * X + np.sin(ridge_angle) * Y

    ridge_mask = (R > R_rim * 0.8) & (s_ridge > 0)
    ridge_elevation = 1.15 * np.exp(-(d_ridge**2) / (2.0 * (1.8**2))) * np.exp(-((s_ridge - 10.0)**2) / (2.0 * (12.0**2)))
    Z[ridge_mask] += ridge_elevation[ridge_mask]

    # 5. Superimposed Micro-Cratering & Regolith Texture
    noise_fine = 0.04 * np.sin(X * 4.0) * np.cos(Y * 4.0) + 0.02 * np.sin(X * 12.0) * np.cos(Y * 12.0)
    Z += noise_fine

    # Build Blender Mesh
    verts = []
    for i in range(grid_size):
        for j in range(grid_size):
            verts.append((float(X[i, j]), float(Y[i, j]), float(Z[i, j])))

    faces = []
    for i in range(grid_size - 1):
        for j in range(grid_size - 1):
            idx = i * grid_size + j
            # Quad faces: (idx, idx+1, idx+grid_size+1, idx+grid_size)
            faces.append((idx, idx + 1, idx + grid_size + 1, idx + grid_size))

    mesh = bpy.data.meshes.new("ShackletonTerrain")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("ShackletonCrater", mesh)
    bpy.context.collection.objects.link(obj)

    # Set Smooth Shading
    for p in mesh.polygons:
        p.use_smooth = True

    # Assign Lunar Regolith Material
    mat = bpy.data.materials.new(name="LunarRegolith")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.16, 0.16, 0.17, 1.0)  # Low lunar albedo ~0.10
        bsdf.inputs["Roughness"].default_value = 0.92                      # Highly diffuse regolith
        bsdf.inputs["Specular IOR Level"].default_value = 0.15              # Low specular
    obj.data.materials.append(mat)

    return obj, Z


def setup_camera():
    """Setup top-down Orthographic Camera framed on Shackleton."""
    cam_data = bpy.data.cameras.new(name="NadirCamera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 30.0  # Covers 30 km domain
    cam_data.clip_start = 0.1
    cam_data.clip_end = 100.0

    cam_obj = bpy.data.objects.new("NadirCamera", cam_data)
    cam_obj.location = (0, 0, 20.0)
    cam_obj.rotation_euler = (0, 0, 0)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    return cam_obj


def setup_sun():
    """Create Sun Light."""
    sun_data = bpy.data.lights.new(name="LunarSun", type='SUN')
    sun_data.energy = 8.0
    sun_data.angle = math.radians(0.5)  # Angular diameter of Sun ~0.5°
    sun_obj = bpy.data.objects.new("LunarSun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    return sun_obj


def set_sun_orientation(sun_obj, incidence_deg=85.0, azimuth_deg=120.0):
    """
    Orient Sun lamp according to lunar solar angles:
    - incidence_deg: 0° is zenith, 85°-89° is grazing South Pole illumination
    - azimuth_deg: angle from North (clockwise)
    """
    elevation_rad = math.radians(90.0 - incidence_deg)
    azimuth_rad = math.radians(azimuth_deg)

    # Direction vector pointing from terrain toward sun
    dx = math.sin(azimuth_rad) * math.cos(elevation_rad)
    dy = math.cos(azimuth_rad) * math.cos(elevation_rad)
    dz = math.sin(elevation_rad)

    # In Blender, a Sun lamp illuminates along its local -Z axis.
    # We rotate the sun to aim along (-dx, -dy, -dz)
    direction = mathutils.Vector((-dx, -dy, -dz))
    rot_quat = direction.to_track_quat('-Z', 'Y')
    sun_obj.rotation_euler = rot_quat.to_euler()


def render_simulated_bundle(sun_obj, incidence_deg, azimuth_deg, filename):
    """Render a 256x256 tile of the schematic mesh at the given illumination angles (not LROC data)."""
    set_sun_orientation(sun_obj, incidence_deg=incidence_deg, azimuth_deg=azimuth_deg)
    
    scene = bpy.context.scene
    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'BW'
    
    out_path = RESULTS_DIR / filename
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print(f"  [Rendered] {filename} (Incidence: {incidence_deg}°, Azimuth: {azimuth_deg}°)")
    return out_path


def export_gltf_model():
    """Export optimized 3D glTF/GLB model for interactive web visualization."""
    glb_path = DOCS_ASSETS_DIR / "shackleton.glb"
    print(f"Exporting optimized 3D model to {glb_path.relative_to(REPO_ROOT)}...")
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format='GLB',
        export_apply=True,
        export_materials='EXPORT',
    )
    print(f"  [Exported] {glb_path.name} ({glb_path.stat().st_size / 1024:.1f} KB)")
    return glb_path


def main():
    print("=" * 70)
    print("  Blender 5.2 Shackleton Crater 3D Procedural Generator & Renderer")
    print("=" * 70)
    clear_scene()

    # 1. Build Physical 3D Mesh
    terrain_obj, Z_data = build_shackleton_mesh(grid_size=160, domain_km=30.0)

    # 2. Setup Lighting & Camera
    cam_obj = setup_camera()
    sun_obj = setup_sun()

    # 3. Render Multi-Illumination Polar Observation Tiles (256x256)
    # Evaluates 4 cardinal solar azimuths at polar grazing incidence (85.0°)
    angles = [
        (85.0, 0.0, "shackleton_inc85_azim000.png"),
        (85.0, 90.0, "shackleton_inc85_azim090.png"),
        (85.0, 180.0, "shackleton_inc85_azim180.png"),
        (85.0, 270.0, "shackleton_inc85_azim270.png"),
        (70.0, 120.0, "shackleton_inc70_azim120.png"),  # Sub-polar comparison
    ]

    print("\nRendering illustrative multi-illumination tiles of the schematic mesh...")
    for inc, azim, fname in angles:
        render_simulated_bundle(sun_obj, inc, azim, fname)

    # 4. Export Web 3D Model
    glb_path = export_gltf_model()

    print("\n[SUCCESS] Shackleton 3D model generation and multi-illumination rendering complete.")


if __name__ == "__main__":
    main()
