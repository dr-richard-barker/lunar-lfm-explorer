"""
lunar_lfm: FAIR Exploration Toolkit for the NASA-IBM Lunar Foundation Model.

Provides zero-synthetic model inspection, modality schemas, acquisition geometry
modeling, benchmark ground truth, and interactive exploration for the ViT-B
multimodal lunar remote sensing model trained on SomBench.
"""

__version__ = "0.1.0"
__author__ = "Richard Barker"
__license__ = "Apache-2.0"

from lunar_lfm.config import (
    HF_MODEL_ID,
    HF_DATASET_ID,
    MODEL_SPECS,
    ScaleFamily,
)
from lunar_lfm.modalities import (
    MODALITIES,
    OPTICAL_METADATA_FIELDS,
    STATIC_CONTEXT_FIELDS,
    ModalityInfo,
    get_modality,
    list_modalities,
    validate_bundle_schema,
)
from lunar_lfm.model_inspect import (
    ModelArchitecture,
    TokenizerSpecs,
    compute_patch_grid,
    estimate_parameter_counts,
)
from lunar_lfm.benchmarks import (
    BENCHMARKS,
    SCIENTIFIC_DISCLOSURES,
    BenchmarkRecord,
    get_benchmark,
    list_benchmarks,
)
from lunar_lfm.hub import LunarHubClient

__all__ = [
    "__version__",
    "HF_MODEL_ID",
    "HF_DATASET_ID",
    "MODEL_SPECS",
    "ScaleFamily",
    "MODALITIES",
    "OPTICAL_METADATA_FIELDS",
    "STATIC_CONTEXT_FIELDS",
    "ModalityInfo",
    "get_modality",
    "list_modalities",
    "validate_bundle_schema",
    "ModelArchitecture",
    "TokenizerSpecs",
    "compute_patch_grid",
    "estimate_parameter_counts",
    "BENCHMARKS",
    "SCIENTIFIC_DISCLOSURES",
    "BenchmarkRecord",
    "get_benchmark",
    "list_benchmarks",
    "LunarHubClient",
]
