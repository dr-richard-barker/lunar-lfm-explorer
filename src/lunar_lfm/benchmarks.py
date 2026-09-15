"""
SomBench benchmark evaluations and scientific disclosures for NASA-IBM LFM.

All benchmark numbers, metrics, standard deviations, and baseline scores are transcribed
directly from the official NASA-IBM Lunar Foundation Model technical report and model card.
Strictly adheres to ABAI L001 (never assert unverified claims) and L006 (no fake numbers).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class BenchmarkRecord:
    """Ground truth record for a SomBench downstream benchmark task."""
    task_id: str
    name: str
    target_object: str
    scale_family: str
    metric_name: str
    metric_direction: str  # "maximize" (↑) or "minimize" (↓)
    best_lfm_score: str
    best_lfm_config: str
    best_baseline_score: str
    best_baseline_name: str
    random_init_lfm_score: str
    key_takeaway: str


BENCHMARKS: Dict[str, BenchmarkRecord] = {
    "robbins_craters_50": BenchmarkRecord(
        task_id="robbins_craters_50",
        name="Robbins Craters (50% Data)",
        target_object="Impact craters on LROC WAC (~100 m/px)",
        scale_family="WAC",
        metric_name="mAP",
        metric_direction="maximize",
        best_lfm_score="0.2541 ± 0.0018",
        best_lfm_config="Full Fine-Tuning",
        best_baseline_score="0.2313 ± 0.0027",
        best_baseline_name="SwinV2-B (ImageNet-22k)",
        random_init_lfm_score="0.2197 ± 0.0027",
        key_takeaway="High label efficiency: LFM with only 50% training data exceeds SwinV2-B trained on 100% data.",
    ),
    "robbins_craters_100": BenchmarkRecord(
        task_id="robbins_craters_100",
        name="Robbins Craters (100% Data)",
        target_object="Impact craters on LROC WAC (~100 m/px)",
        scale_family="WAC",
        metric_name="mAP",
        metric_direction="maximize",
        best_lfm_score="0.2581 ± 0.0017",
        best_lfm_config="LoRA (rank 16, α=32)",
        best_baseline_score="0.2420 ± 0.0047",
        best_baseline_name="SwinV2-B (ImageNet-22k)",
        random_init_lfm_score="0.2289 ± 0.0037",
        key_takeaway="LoRA fine-tuning outperforms full fine-tuning with narrower seed spread.",
    ),
    "nac_craters_meter_scale": BenchmarkRecord(
        task_id="nac_craters_meter_scale",
        name="NAC Craters (Meter Scale)",
        target_object="Small impact craters on LROC NAC (1 m/px)",
        scale_family="NAC",
        metric_name="mAP",
        metric_direction="maximize",
        best_lfm_score="0.1543 ± 0.0098",
        best_lfm_config="LoRA (rank 16, α=32)",
        best_baseline_score="0.1552 ± 0.0086",
        best_baseline_name="SwinV2-B",
        random_init_lfm_score="0.1274 ± 0.0151",
        key_takeaway="Leaders are comparable within seed spread; frozen encoder fails, requiring adapter adaptation.",
    ),
    "irregular_mare_patches": BenchmarkRecord(
        task_id="irregular_mare_patches",
        name="Irregular Mare Patches (IMP)",
        target_object="Young volcanic surface features / enigmatic mounds",
        scale_family="NAC/WAC",
        metric_name="IoU₁",
        metric_direction="maximize",
        best_lfm_score="0.5709 ± 0.0114",
        best_lfm_config="Frozen Encoder",
        best_baseline_score="0.5687 ± 0.0181",
        best_baseline_name="ConvNeXtV2-B",
        random_init_lfm_score="0.3142 ± 0.0746",
        key_takeaway="Pretraining is essential: random-init control collapses to 0.3142. Frozen encoder yields strongest generalization.",
    ),
    "polar_ice_prospectivity": BenchmarkRecord(
        task_id="polar_ice_prospectivity",
        name="Polar Ice Prospectivity",
        target_object="Permanently Shadowed Regions (PSRs) ice stability",
        scale_family="WAC/Context",
        metric_name="RMSE",
        metric_direction="minimize",
        best_lfm_score="0.0293 ± 0.0013",
        best_lfm_config="Full Fine-Tuning",
        best_baseline_score="0.0377 ± 0.0004",
        best_baseline_name="SwinV2-B",
        random_init_lfm_score="0.0397 ± 0.0004",
        key_takeaway="Widest margin: 22% RMSE reduction. Modality late fusion with only 3 modalities (aspect, slope, DICE) matches full-stack ConvNeXt-B.",
    ),
}

# Explicit Scientific & Operational Disclosures (Grounded in Model Card)
SCIENTIFIC_DISCLOSURES: List[Dict[str, str]] = [
    {
        "category": "Geodetic Reference Frame",
        "statement": "The model maintains NO geodetic reference frame. It captures local topographic shape and relative gradients, but absolute elevation has an offset shift, and generated coordinates can drift by tens of degrees.",
        "severity": "CRITICAL_LIMITATION",
    },
    {
        "category": "Ice Prospectivity Target",
        "statement": "Ice-prospectivity outputs regress a knowledge-driven fuzzy-overlay prospectivity target, NOT direct in-situ water ice measurements.",
        "severity": "SCIENTIFIC_CAUTION",
    },
    {
        "category": "Operational Certification",
        "statement": "The model is NOT certified for operational mission decisions such as landing-site certification, terrain hazard clearance, or rover traverse path clearance.",
        "severity": "OPERATIONAL_BOUNDARY",
    },
    {
        "category": "Cross-Modal Generation",
        "statement": "Any-to-any multimodal reconstructions are qualitative probes of cross-modal latent alignment, NOT calibrated radiometry or photogrammetry.",
        "severity": "METHODOLOGY_NOTE",
    },
]


def list_benchmarks() -> List[BenchmarkRecord]:
    """List all benchmark records."""
    return list(BENCHMARKS.values())


def get_benchmark(task_id: str) -> Optional[BenchmarkRecord]:
    """Retrieve benchmark record by task identifier."""
    return BENCHMARKS.get(task_id)
