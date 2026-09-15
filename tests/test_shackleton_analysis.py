"""
Unit tests for Shackleton Crater Artemis IV landing site analysis.
"""

from scripts.analyze_shackleton_artemis4 import SHACKLETON_SPECS, CANDIDATE_ZONES


def test_shackleton_physical_parameters():
    """Verify grounded physical geometry of Shackleton Crater."""
    assert abs(SHACKLETON_SPECS["center_latitude_deg"] - (-89.9)) < 0.1
    assert abs(SHACKLETON_SPECS["rim_diameter_km"] - 21.0) < 0.1
    assert abs(SHACKLETON_SPECS["crater_depth_km"] - 4.2) < 0.1
    assert SHACKLETON_SPECS["psr_floor_temperature_kelvin"] == 40.0


def test_candidate_zones_integrity():
    """Verify candidate zones have valid coordinates, slopes, and illumination."""
    assert len(CANDIDATE_ZONES) >= 4

    for zone in CANDIDATE_ZONES:
        # Latitudes must be in South Polar region (< -89.0°)
        assert zone["latitude_deg"] < -89.0

        # Slopes must sum to ~100%
        slopes = zone["slope_distribution"]
        total_slope = (
            slopes["safe_under_10deg_pct"]
            + slopes["marginal_10_to_15deg_pct"]
            + slopes["hazard_over_15deg_pct"]
        )
        assert abs(total_slope - 100.0) < 0.5

        # Annual illumination must be bounded [0, 100]
        illum = zone["annual_illumination_pct"]
        assert illum["mean"] > 70.0
        assert illum["maximum"] <= 100.0

        # DTE communication line-of-sight must be positive
        assert zone["dte_visibility_pct"] > 80.0

        # Distance to PSR cold trap must be positive
        assert zone["distance_to_psr_cold_trap_km"] > 0.0

        # QuickMap URL must be valid
        assert zone["quickmap_url"].startswith("https://quickmap.lroc.im-ldi.com/")


if __name__ == "__main__":
    test_shackleton_physical_parameters()
    test_candidate_zones_integrity()
    print("All Shackleton analysis tests passed.")
