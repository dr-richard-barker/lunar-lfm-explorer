"""
Unit tests for the schematic Blender Shackleton model and its render inventory.
Validates glTF model size (ABAI L022), render resolution, and that the inventory claims no model run.
Standard library only (zero external dependencies).
"""

import json
import struct
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def _get_png_dimensions(file_path: Path):
    """Extract width and height from PNG IHDR chunk using standard library struct."""
    with open(file_path, "rb") as f:
        header = f.read(24)
        if header[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"{file_path} is not a valid PNG")
        width, height = struct.unpack(">II", header[16:24])
        return width, height


def test_shackleton_glb_asset():
    """Verify exported glTF/GLB model exists and complies with repo weight bounds (ABAI L022)."""
    glb_path = ROOT_DIR / "docs" / "assets" / "shackleton.glb"
    assert glb_path.exists(), f"Missing 3D model asset: {glb_path}"

    size_bytes = glb_path.stat().st_size
    assert size_bytes > 100_000, f"GLB file unexpectedly small ({size_bytes} bytes)"
    assert size_bytes < 3_000_000, f"GLB file exceeds 3 MB limit (ABAI L022): {size_bytes} bytes"


def test_blender_render_tiles():
    """Verify rendered tiles are 256x256 px PNGs (the model's input size)."""
    assets_dir = ROOT_DIR / "docs" / "assets" / "blender_renders"
    results_dir = ROOT_DIR / "results" / "blender_renders"

    expected_tiles = [
        "shackleton_inc85_azim000.png",
        "shackleton_inc85_azim090.png",
        "shackleton_inc85_azim180.png",
        "shackleton_inc85_azim270.png",
        "shackleton_inc70_azim120.png",
    ]

    for tile_name in expected_tiles:
        for folder in [assets_dir, results_dir]:
            tile_path = folder / tile_name
            assert tile_path.exists(), f"Missing render tile {tile_path}"

            width, height = _get_png_dimensions(tile_path)
            assert (width, height) == (256, 256), f"Tile {tile_name} has unexpected dimensions ({width}, {height})"


def test_blender_render_inventory():
    """results/blender_render_inventory.json records tiles and grids, and claims no model run."""
    json_path = ROOT_DIR / "results" / "blender_render_inventory.json"
    assert json_path.exists(), f"Missing inventory: {json_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["model_inference_run"] is False
    assert len(data["tiles"]) == 5
    for tile in data["tiles"]:
        assert (tile["width_px"], tile["height_px"]) == (256, 256)
    assert data["flexivit_patch_grids_256px"]["p16"]["patches_per_modality"] == 256

    # No model-performance figures may appear in an inventory of renders.
    text = json.dumps(data).lower()
    for banned in ("disambiguation", "divergence", "gain", "qualified"):
        assert banned not in text, f"Inventory contains model-performance wording: {banned}"


def test_mesh_specs_match_blender_script():
    """The relief stated for the schematic mesh is the one the Blender script builds."""
    import re
    import sys
    sys.path.insert(0, str(ROOT_DIR))
    from scripts.inventory_blender_renders import MESH_SPECS

    src = (ROOT_DIR / "scripts" / "blender" / "generate_shackleton_3d.py").read_text(encoding="utf-8")
    def const(name):
        m = re.search(rf"^\s*{name}\s*=\s*(-?[0-9.]+)", src, re.M)
        assert m, f"{name} not found in generate_shackleton_3d.py"
        return float(m.group(1))

    assert const("R_rim") == MESH_SPECS["rim_radius_km"]
    assert const("R_floor") == MESH_SPECS["floor_radius_km"]
    assert const("Z_rim") == MESH_SPECS["rim_elevation_km"]
    assert const("Z_floor") == MESH_SPECS["floor_elevation_km"]
    assert abs((const("Z_rim") - const("Z_floor")) - MESH_SPECS["relief_km"]) < 1e-9


if __name__ == "__main__":
    test_shackleton_glb_asset()
    test_blender_render_tiles()
    test_blender_render_inventory()
    test_mesh_specs_match_blender_script()
    print("All Blender pipeline tests passed.")
