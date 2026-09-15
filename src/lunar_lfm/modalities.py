"""
Modality registry and schema validation for the NASA-IBM Lunar Foundation Model.

The model operates across 11 modalities (9 dense image-like, 2 sequence-like context)
split into two scale families:
  - WAC family: 51.2 km tiles at ~100 m/px
  - NAC family: 512 m tiles at ~1 m/px

Acquisition geometry and static context are tokenized as sequence inputs.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from lunar_lfm.config import ScaleFamily


@dataclass(frozen=True)
class ModalityInfo:
    """Metadata specification for a SomBench modality."""
    key: str
    name: str
    family: ScaleFamily
    channels: int
    native_resolution_m: float
    source_instrument: str
    description: str
    channel_names: Tuple[str, ...]
    is_dense: bool = True


# The 9 Dense Modalities (5 WAC, 4 NAC)
MODALITIES: Dict[str, ModalityInfo] = {
    # WAC Family (51.2 km footprint)
    "vis": ModalityInfo(
        key="vis",
        name="WAC Visible Reflectance",
        family=ScaleFamily.WAC,
        channels=5,
        native_resolution_m=100.0,
        source_instrument="LROC WAC",
        description="5 visible reflectance color bands (415, 566, 604, 643, 689 nm)",
        channel_names=("band_415nm", "band_566nm", "band_604nm", "band_643nm", "band_689nm"),
        is_dense=True,
    ),
    "uv": ModalityInfo(
        key="uv",
        name="WAC Ultraviolet Reflectance",
        family=ScaleFamily.WAC,
        channels=2,
        native_resolution_m=500.0,
        source_instrument="LROC WAC",
        description="2 ultraviolet reflectance bands (321, 360 nm)",
        channel_names=("band_321nm", "band_360nm"),
        is_dense=True,
    ),
    "dtm": ModalityInfo(
        key="dtm",
        name="WAC Digital Terrain Model",
        family=ScaleFamily.WAC,
        channels=1,
        native_resolution_m=60.0,
        source_instrument="SLDEM2015",
        description="Global digital elevation model from combined LRO LOLA and Kaguya TC",
        channel_names=("elevation",),
        is_dense=True,
    ),
    "slope": ModalityInfo(
        key="slope",
        name="WAC Terrain Slope",
        family=ScaleFamily.WAC,
        channels=1,
        native_resolution_m=60.0,
        source_instrument="SLDEM2015",
        description="Surface topographic slope derived from SLDEM2015",
        channel_names=("slope_deg",),
        is_dense=True,
    ),
    "aspect": ModalityInfo(
        key="aspect",
        name="WAC Terrain Aspect",
        family=ScaleFamily.WAC,
        channels=2,
        native_resolution_m=60.0,
        source_instrument="SLDEM2015",
        description="Surface slope azimuth direction stored as sin/cos pair to avoid angular 0/360 wrap-around",
        channel_names=("sin_aspect", "cos_aspect"),
        is_dense=True,
    ),

    # NAC Family (512 m footprint)
    "nac": ModalityInfo(
        key="nac",
        name="NAC Panchromatic Imagery",
        family=ScaleFamily.NAC,
        channels=1,
        native_resolution_m=1.0,
        source_instrument="LROC NAC",
        description="High-resolution panchromatic visible imagery (0.5 to 2.0 m/pixel)",
        channel_names=("panchromatic",),
        is_dense=True,
    ),
    "dtm_3m": ModalityInfo(
        key="dtm_3m",
        name="NAC Stereo DTM",
        family=ScaleFamily.NAC,
        channels=1,
        native_resolution_m=3.0,
        source_instrument="NAC-stereo DTM",
        description="High-resolution 3m stereo photogrammetric elevation model",
        channel_names=("elevation_3m",),
        is_dense=True,
    ),
    "slope_3m": ModalityInfo(
        key="slope_3m",
        name="NAC High-Res Slope",
        family=ScaleFamily.NAC,
        channels=1,
        native_resolution_m=3.0,
        source_instrument="NAC-stereo DTM",
        description="Meter-scale topographic slope derived from 3m stereo DTM",
        channel_names=("slope_3m_deg",),
        is_dense=True,
    ),
    "aspect_3m": ModalityInfo(
        key="aspect_3m",
        name="NAC High-Res Aspect",
        family=ScaleFamily.NAC,
        channels=2,
        native_resolution_m=3.0,
        source_instrument="NAC-stereo DTM",
        description="Meter-scale slope aspect stored as sin/cos pair to avoid angular wrap-around",
        channel_names=("sin_aspect_3m", "cos_aspect_3m"),
        is_dense=True,
    ),
}

# The 8 Optical Metadata Context Fields
OPTICAL_METADATA_FIELDS: Tuple[Dict[str, str], ...] = (
    {"key": "solar_incidence", "unit": "degrees", "desc": "Solar incidence angle at tile acquisition"},
    {"key": "emission_angle", "unit": "degrees", "desc": "Spacecraft emission viewing angle"},
    {"key": "phase_angle", "unit": "degrees", "desc": "Phase angle between sun, target, and spacecraft"},
    {"key": "solar_azimuth", "unit": "degrees", "desc": "Azimuth direction of illumination"},
    {"key": "subsolar_lat", "unit": "degrees_north", "desc": "Subsolar point latitude"},
    {"key": "subsolar_lon", "unit": "degrees_east", "desc": "Subsolar point longitude"},
    {"key": "center_lat", "unit": "degrees_north", "desc": "Tile center latitude"},
    {"key": "center_lon", "unit": "degrees_east", "desc": "Tile center longitude"},
)

# The 28 Static-Map Context Fields (Footprint Averages)
STATIC_CONTEXT_FIELDS: Tuple[Dict[str, str], ...] = (
    # Diviner Thermophysics (5)
    {"key": "TREG", "instrument": "LRO Diviner", "desc": "Regolith surface temperature model"},
    {"key": "TBOL", "instrument": "LRO Diviner", "desc": "Bolometric brightness temperature"},
    {"key": "ROCK_ABUND", "instrument": "LRO Diviner", "desc": "Surface rock abundance fraction"},
    {"key": "HPAR", "instrument": "LRO Diviner", "desc": "Thermal parameter H (scale depth)"},
    {"key": "DICE", "instrument": "LRO Diviner", "desc": "Depth to ice stability / ice prospectivity index"},
    # LOLA Altimeter & Surface Metrics (4)
    {"key": "ROUGHNESS", "instrument": "LRO LOLA", "desc": "Kilometer-scale surface roughness"},
    {"key": "PSR", "instrument": "LRO LOLA", "desc": "Permanently Shadowed Region flag/coverage"},
    {"key": "AVG_ILLUM", "instrument": "LRO LOLA", "desc": "Annual average solar illumination fraction"},
    {"key": "ALBEDO", "instrument": "LRO LOLA", "desc": "Normal albedo at 1064 nm"},
    # Mini-RF Synthetic Aperture Radar (3)
    {"key": "MINIRF_CPR", "instrument": "Mini-RF", "desc": "Circular Polarization Ratio (ice vs rough blockiness)"},
    {"key": "MINIRF_S1", "instrument": "Mini-RF", "desc": "Total backscattered Stokes power"},
    {"key": "MINIRF_DOP", "instrument": "Mini-RF", "desc": "Degree of Polarization"},
    # Kaguya / SELENE Spectral Mineralogy (3)
    {"key": "MI_MINERAL", "instrument": "Kaguya MI", "desc": "Multiband Imager mineral composition index"},
    {"key": "SW_FE", "instrument": "Kaguya SP", "desc": "Spectral Profiler estimated FeO weight percent"},
    {"key": "SP_MINER", "instrument": "Kaguya SP", "desc": "Plagioclase / pyroxene / olivine mineral map index"},
    # LROC WAC Color & Compositional Indexes (3)
    {"key": "nr643", "instrument": "LROC WAC", "desc": "Normalized reflectance at 643 nm"},
    {"key": "TIO2", "instrument": "LROC WAC", "desc": "Estimated TiO2 abundance map"},
    {"key": "WAC_MATURITY", "instrument": "LROC WAC", "desc": "Optical maturity parameter (OMAT)"},
    # GRAIL Gravity Model (1)
    {"key": "GRAVITY", "instrument": "GRAIL", "desc": "Bouguer gravity anomaly / crustal density variation"},
    # Lunar Prospector Neutron Spectrometer (1)
    {"key": "HYDROGEN", "instrument": "Lunar Prospector", "desc": "Epithermal neutron flux / hydrogen enrichment"},
    # Additional Contextual Channels (8)
    {"key": "SLOPE_MEAN", "instrument": "SLDEM2015", "desc": "Tile-mean topographic slope"},
    {"key": "SLOPE_STD", "instrument": "SLDEM2015", "desc": "Tile slope standard deviation"},
    {"key": "ELEVATION_MEAN", "instrument": "SLDEM2015", "desc": "Tile-mean elevation above lunar sphere (1737.4 km)"},
    {"key": "ELEVATION_MIN", "instrument": "SLDEM2015", "desc": "Tile minimum elevation"},
    {"key": "ELEVATION_MAX", "instrument": "SLDEM2015", "desc": "Tile maximum elevation"},
    {"key": "MAX_SURF_TEMP", "instrument": "LRO Diviner", "desc": "Maximum annual surface temperature"},
    {"key": "MIN_SURF_TEMP", "instrument": "LRO Diviner", "desc": "Minimum annual surface temperature"},
    {"key": "SUB_SURF_TEMP", "instrument": "LRO Diviner", "desc": "Predicted temperature at 1m depth"},
)


def get_modality(key: str) -> Optional[ModalityInfo]:
    """Retrieve metadata for a given modality key."""
    return MODALITIES.get(key)


def list_modalities(family: Optional[ScaleFamily] = None) -> List[ModalityInfo]:
    """List all modalities, optionally filtered by scale family."""
    if family is None:
        return list(MODALITIES.values())
    return [m for m in MODALITIES.values() if m.family == family]


def validate_bundle_schema(bundle_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that a given data bundle dictionary conforms to the SomBench specification.
    Returns (is_valid, error_messages).
    """
    errors: List[str] = []
    if not isinstance(bundle_dict, dict):
        return False, ["Bundle must be a dictionary"]

    family_str = bundle_dict.get("scale_family")
    if family_str not in [ScaleFamily.WAC.value, ScaleFamily.NAC.value]:
        errors.append(f"Invalid or missing 'scale_family': {family_str}. Must be 'WAC' or 'NAC'.")
        return False, errors

    family = ScaleFamily(family_str)
    expected_modalities = list_modalities(family)

    # Check for presence of required modalities
    modalities_data = bundle_dict.get("modalities", {})
    for mod in expected_modalities:
        if mod.key not in modalities_data:
            errors.append(f"Missing expected modality '{mod.key}' for family {family.value}")
        else:
            shape = modalities_data[mod.key].get("shape")
            if not shape or len(shape) != 3:
                errors.append(f"Modality '{mod.key}' must define a 3D shape (C, H, W)")
            elif shape[0] != mod.channels:
                errors.append(
                    f"Modality '{mod.key}' channel mismatch: got {shape[0]}, expected {mod.channels}"
                )

    # Check optical metadata fields
    opt_meta = bundle_dict.get("optical_metadata", {})
    for field in OPTICAL_METADATA_FIELDS:
        if field["key"] not in opt_meta:
            errors.append(f"Missing optical metadata field: '{field['key']}'")

    return len(errors) == 0, errors
