#!/usr/bin/env python3
"""
Inventory of the Blender-rendered Shackleton-like tiles and FlexiViT patch grids.

Replaces scripts/test_lfm_shackleton_blender.py, which wrote a "+38.7% shadow disambiguation
gain" and divergence figures that were typed into the script ("Simulated") rather than
computed: it loaded the model but never ran it.

This script runs no model. It records what can be read from the files themselves:
- each rendered tile's size and the lighting it was rendered with;
- the geometry parameters of the schematic mesh (scripts/blender/generate_shackleton_3d.py);
- FlexiViT patch grids for a 256 x 256 input, from lunar_lfm.model_inspect.

The mesh is an analytic bowl with a smooth ridge, not LOLA/SLDEM2015 terrain, and the lighting
is illustrative: at Shackleton's latitude (89.67°S, IAU) the Sun is never more than about
0.33° + 1.54° ≈ 1.9° above the horizon, so the 85° and 70° incidence renders do not occur there.

Output:
- results/blender_render_inventory.json
"""

import json
import struct
import sys
from pathlib import Path
from typing import Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from lunar_lfm.model_inspect import ModelArchitecture  # noqa: E402

RENDERS_DIR = REPO_ROOT / "results" / "blender_renders"
RESULTS_FILE = REPO_ROOT / "results" / "blender_render_inventory.json"

# Geometry of the schematic mesh; must match build_shackleton_mesh() in
# scripts/blender/generate_shackleton_3d.py (checked by tests/test_blender_pipeline.py).
MESH_SPECS = {
    "geometry": "analytic bowl + Gaussian ridge at 135 deg azimuth; not derived from LOLA/SLDEM2015",
    "domain_km": 30.0,
    "grid_vertices": 160,
    "rim_radius_km": 10.5,
    "floor_radius_km": 3.5,
    "rim_elevation_km": 1.2,
    "floor_elevation_km": -3.8,
    "relief_km": 5.0,
    "ridge_peak_km": 1.15,
}

TILES = [
    ("shackleton_inc85_azim000.png", 85.0, 0.0),
    ("shackleton_inc85_azim090.png", 85.0, 90.0),
    ("shackleton_inc85_azim180.png", 85.0, 180.0),
    ("shackleton_inc85_azim270.png", 85.0, 270.0),
    ("shackleton_inc70_azim120.png", 70.0, 120.0),
]


def png_dimensions(path: Path) -> Tuple[int, int]:
    """Read PNG width and height from the IHDR chunk (standard library only)."""
    with open(path, "rb") as f:
        head = f.read(24)
    if len(head) < 24 or not head.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"Not a PNG file: {path}")
    w, h = struct.unpack(">II", head[16:24])
    return int(w), int(h)


def main() -> None:
    tiles = []
    for name, incidence, azimuth in TILES:
        path = RENDERS_DIR / name
        if not path.exists():
            sys.exit(f"Missing render {name}; run scripts/blender/generate_shackleton_3d.py first.")
        w, h = png_dimensions(path)
        tiles.append({
            "file": str(path.relative_to(REPO_ROOT)),
            "solar_incidence_deg": incidence,
            "solar_elevation_deg": round(90.0 - incidence, 1),
            "solar_azimuth_deg": azimuth,
            "width_px": w,
            "height_px": h,
            "size_bytes": path.stat().st_size,
        })

    arch = ModelArchitecture()
    grids = {}
    for p in (8, 16, 32):
        gh, gw, n = arch.compute_patch_grid((p, p))
        grids[f"p{p}"] = {"patch_size": p, "grid": f"{gh}x{gw}", "patches_per_modality": n}

    inventory = {
        "model_inference_run": False,
        "note": (
            "Renders of a schematic mesh with illustrative lighting. They are not LROC data "
            "and were not passed through the NASA-IBM LFM."
        ),
        "mesh_specs": MESH_SPECS,
        "tiles": tiles,
        "flexivit_patch_grids_256px": grids,
    }
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
        f.write("\n")
    print(f"Wrote {RESULTS_FILE.relative_to(REPO_ROOT)} ({len(tiles)} tiles)")


if __name__ == "__main__":
    main()
