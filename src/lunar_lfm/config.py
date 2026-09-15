"""
Core configuration constants and schemas for the NASA-IBM Lunar Foundation Model.
All constants are grounded in the official Hugging Face model card and technical report:
https://huggingface.co/nasa-ibm-ai4science/NASA-IBM-Lunar-Foundation-Model
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Tuple


HF_MODEL_ID = "nasa-ibm-ai4science/NASA-IBM-Lunar-Foundation-Model"
HF_DATASET_ID = "nasa-ibm-ai4science/Sombench-pretraining-data"
HF_COLLECTION_URL = "https://huggingface.co/collections/nasa-ibm-ai4science/lunar-fm-ml-ready-benchmark-dataset-sombench"
UPSTREAM_GITHUB_URL = "https://github.com/NASA-IMPACT/NASA-IBM-Lunar-Foundation-Model"
TECHNICAL_REPORT_URL = "https://huggingface.co/nasa-ibm-ai4science/NASA-IBM-Lunar-Foundation-Model/blob/main/NI_LFM_Technical_Report.pdf"


class ScaleFamily(str, Enum):
    """Spatial resolution scale families in SomBench."""
    WAC = "WAC"  # Wide Angle Camera: ~100 m/px, 51.2 km tile footprint
    NAC = "NAC"  # Narrow Angle Camera: ~1 m/px, 512 m tile footprint


@dataclass(frozen=True)
class ModelSpecs:
    """Ground-truth architecture specifications for NASA-IBM LFM."""
    backbone_type: str = "ViT-B"
    embed_dim: int = 768
    depth: int = 12
    num_heads: int = 12
    mlp_ratio: float = 4.0
    input_size: Tuple[int, int] = (256, 256)
    pretrain_patch_size: Tuple[int, int] = (16, 16)
    downstream_patch_size: Tuple[int, int] = (8, 8)
    decoder_depth: int = 12
    decoder_heads: int = 12
    decoder_embed_dim: int = 768
    fsq_levels: Tuple[int, ...] = (8, 8, 8, 6, 5)  # 8*8*8*6*5 = 15,360 codebook states
    pretrain_hardware: str = "16 x NVIDIA H100"
    pretrain_steps: int = 150_000
    pretrain_global_batch: int = 1536
    pretrain_precision: str = "bfloat16"
    pretrain_gpu_hours: int = 1100
    sombench_wac_bundles: int = 963_609
    sombench_nac_bundles: int = 1_000_113
    total_sombench_bundles: int = 1_963_722
    dense_modalities_count: int = 9
    sequence_modalities_count: int = 2
    total_modalities_count: int = 11


MODEL_SPECS = ModelSpecs()
