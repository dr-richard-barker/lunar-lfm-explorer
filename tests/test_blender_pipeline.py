"""
Unit tests for Blender 3D Shackleton Crater physical modeling and LFM test-run pipeline.
Validates 3D glTF model size (ABAI L022), render resolution, and scientific metrics.
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
    """Verify rendered tiles are 256x256 px PNGs suitable for LFM ViT input."""
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


def test_blender_lfm_test_run_schema():
    """Verify schema and empirical metrics of results/blender_lfm_test_run.json."""
    json_path = ROOT_DIR / "results" / "blender_lfm_test_run.json"
    assert json_path.exists(), f"Missing test-run output: {json_path}"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "model_id" in data
    assert "blender_mesh_specs" in data
    assert data["blender_mesh_specs"]["crater_diameter_km"] == 21.0
    assert data["blender_mesh_specs"]["relief_depth_km"] == 4.2

    assert len(data["tiles_evaluated"]) == 5
    for tile in data["tiles_evaluated"]:
        assert len(tile["optical_vector"]) == 8

    # FlexiViT tokenization specs
    assert "flexivit_tokenization" in data
    for p in ["p8", "p16", "p32"]:
        assert p in data["flexivit_tokenization"]

    # Shadow disambiguation stability gain
    metrics = data["shadow_disambiguation_metrics"]
    assert metrics["shadow_disambiguation_gain_pct"] > 30.0
    assert metrics["lfm_sequence_conditioned_divergence_pct"] < 10.0
    assert metrics["illumination_blind_baseline_divergence_pct"] > 35.0


if __name__ == "__main__":
    test_shackleton_glb_asset()
    test_blender_render_tiles()
    test_blender_lfm_test_run_schema()
    print("All Blender pipeline tests passed.")
