"""
Unit tests for SomBench benchmark ground truth records and scientific disclosures.
"""

try:
    import pytest
except ImportError:
    pytest = None

from lunar_lfm.benchmarks import (
    BENCHMARKS,
    SCIENTIFIC_DISCLOSURES,
    get_benchmark,
    list_benchmarks,
)


def test_benchmarks_integrity():
    """Verify all 5 official benchmarks are registered with metrics and baselines."""
    benchmarks = list_benchmarks()
    assert len(benchmarks) == 5

    # Check Robbins 50%
    r50 = get_benchmark("robbins_craters_50")
    assert r50 is not None
    assert "0.2541" in r50.best_lfm_score
    assert "SwinV2-B" in r50.best_baseline_name
    assert r50.metric_name == "mAP"

    # Check Robbins 100%
    r100 = get_benchmark("robbins_craters_100")
    assert r100 is not None
    assert "LoRA" in r100.best_lfm_config
    assert "0.2581" in r100.best_lfm_score

    # Check Polar Ice Prospectivity
    ice = get_benchmark("polar_ice_prospectivity")
    assert ice is not None
    assert ice.metric_direction == "minimize"
    assert "0.0293" in ice.best_lfm_score
    assert "0.0377" in ice.best_baseline_score

    # Check IMP
    imp = get_benchmark("irregular_mare_patches")
    assert imp is not None
    assert "Frozen Encoder" in imp.best_lfm_config
    assert "0.5709" in imp.best_lfm_score


def test_scientific_disclosures():
    """Verify required ABAI scientific disclosures are present and categorized."""
    assert len(SCIENTIFIC_DISCLOSURES) == 4
    severities = [d["severity"] for d in SCIENTIFIC_DISCLOSURES]
    assert "CRITICAL_LIMITATION" in severities
    assert "SCIENTIFIC_CAUTION" in severities
    assert "OPERATIONAL_BOUNDARY" in severities

    # Check geodetic frame disclosure
    geodetic = next(d for d in SCIENTIFIC_DISCLOSURES if "Geodetic" in d["category"])
    assert "maintains NO geodetic reference frame" in geodetic["statement"]
