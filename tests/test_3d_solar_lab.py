"""
Unit tests for 3D Solar Lab multi-illumination physical models and web integration.
Validates 3D glTF model sizes (ABAI L022), binary headers, and HTML/JS integration.
Standard library only (zero external dependencies).
"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

EXPECTED_3D_MODELS = [
    "shackleton_3d_inc85_azim000.glb",
    "shackleton_3d_inc85_azim090.glb",
    "shackleton_3d_inc85_azim180.glb",
    "shackleton_3d_inc85_azim270.glb",
    "shackleton_3d_inc70_azim120.glb",
    "shackleton_3d_neutral.glb",
]


def test_3d_models_exist_and_sizes():
    """Verify all 6 multi-illumination 3D models exist and respect ABAI L022 size bounds."""
    docs_3d = ROOT_DIR / "docs" / "assets" / "3d"
    assert docs_3d.exists(), f"Directory missing: {docs_3d}"

    for model_name in EXPECTED_3D_MODELS:
        p = docs_3d / model_name
        assert p.exists(), f"Missing 3D model: {p}"
        size = p.stat().st_size
        assert size > 100_000, f"Model {model_name} unexpectedly small ({size} bytes)"
        assert size < 3_000_000, f"Model {model_name} exceeds 3 MB limit (ABAI L022): {size} bytes"


def test_gltf_binary_header():
    """Verify all 3D models have valid glTF 2.0 binary headers (magic bytes 'glTF')."""
    docs_3d = ROOT_DIR / "docs" / "assets" / "3d"
    for model_name in EXPECTED_3D_MODELS:
        p = docs_3d / model_name
        with open(p, "rb") as f:
            magic = f.read(4)
            assert magic == b"glTF", f"File {model_name} lacks glTF magic bytes"


def test_3d_solar_lab_html_integration():
    """Verify docs/index.html integrates the 3D Solar Lab tab and model viewer elements."""
    html_path = ROOT_DIR / "docs" / "index.html"
    assert html_path.exists()

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert 'data-tab="tab-3d-lab"' in html, "Missing 3D Solar Lab nav-tab button"
    assert 'id="tab-3d-lab"' in html, "Missing tab-3d-lab section container"
    assert 'id="lab-3d-model-viewer"' in html, "Missing 3D model viewer element"
    assert 'id="lab-3d-angle-buttons"' in html, "Missing angle selector button group"

    for model_name in EXPECTED_3D_MODELS:
        assert model_name in html, f"Model {model_name} not referenced in HTML buttons"


def test_3d_solar_lab_js_registration():
    """Verify docs/app.js registers and defines init3DSolarLab."""
    js_path = ROOT_DIR / "docs" / "app.js"
    assert js_path.exists()

    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()

    assert "init3DSolarLab();" in js, "init3DSolarLab not invoked in DOMContentLoaded"
    assert "function init3DSolarLab()" in js, "function init3DSolarLab not defined"


if __name__ == "__main__":
    test_3d_models_exist_and_sizes()
    test_gltf_binary_header()
    test_3d_solar_lab_html_integration()
    test_3d_solar_lab_js_registration()
    print("All 3D Solar Lab tests passed.")
