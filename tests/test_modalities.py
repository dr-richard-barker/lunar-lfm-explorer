"""
Unit tests for SomBench modality registry and schema validation.
"""

try:
    import pytest
except ImportError:
    pytest = None

from lunar_lfm.config import ScaleFamily
from lunar_lfm.modalities import (
    MODALITIES,
    OPTICAL_METADATA_FIELDS,
    STATIC_CONTEXT_FIELDS,
    get_modality,
    list_modalities,
    validate_bundle_schema,
)


def test_modality_counts():
    """Verify total modality counts and scale family distribution."""
    assert len(MODALITIES) == 9
    wac_mods = list_modalities(ScaleFamily.WAC)
    nac_mods = list_modalities(ScaleFamily.NAC)
    assert len(wac_mods) == 5
    assert len(nac_mods) == 4
    assert len(OPTICAL_METADATA_FIELDS) == 8
    assert len(STATIC_CONTEXT_FIELDS) == 28


def test_modality_channels_and_resolutions():
    """Verify channel configurations and resolutions match SomBench specifications."""
    vis = get_modality("vis")
    assert vis is not None
    assert vis.channels == 5
    assert vis.native_resolution_m == 100.0

    uv = get_modality("uv")
    assert uv is not None
    assert uv.channels == 2
    assert uv.native_resolution_m == 500.0

    dtm = get_modality("dtm")
    assert dtm is not None
    assert dtm.channels == 1
    assert dtm.native_resolution_m == 60.0

    # Aspect must be sin/cos pair (2 channels)
    aspect = get_modality("aspect")
    assert aspect is not None
    assert aspect.channels == 2
    assert "sin_aspect" in aspect.channel_names
    assert "cos_aspect" in aspect.channel_names

    nac = get_modality("nac")
    assert nac is not None
    assert nac.channels == 1
    assert nac.native_resolution_m == 1.0

    aspect_3m = get_modality("aspect_3m")
    assert aspect_3m is not None
    assert aspect_3m.channels == 2


def test_bundle_schema_validation_valid():
    """Verify valid WAC and NAC bundle schemas pass validation."""
    valid_wac = {
        "scale_family": "WAC",
        "modalities": {
            "vis": {"shape": [5, 256, 256]},
            "uv": {"shape": [2, 256, 256]},
            "dtm": {"shape": [1, 256, 256]},
            "slope": {"shape": [1, 256, 256]},
            "aspect": {"shape": [2, 256, 256]},
        },
        "optical_metadata": {f["key"]: 45.0 for f in OPTICAL_METADATA_FIELDS},
    }
    is_valid, errors = validate_bundle_schema(valid_wac)
    assert is_valid is True
    assert len(errors) == 0


def test_bundle_schema_validation_invalid():
    """Verify invalid channel numbers and missing modalities fail with explicit errors."""
    invalid_bundle = {
        "scale_family": "WAC",
        "modalities": {
            "vis": {"shape": [3, 256, 256]},  # Wrong: should be 5
            # Missing uv, dtm, slope, aspect
        },
        "optical_metadata": {},  # Missing optical fields
    }
    is_valid, errors = validate_bundle_schema(invalid_bundle)
    assert is_valid is False
    assert any("channel mismatch" in e for e in errors)
    assert any("Missing expected modality 'uv'" in e for e in errors)
    assert any("Missing optical metadata field" in e for e in errors)
