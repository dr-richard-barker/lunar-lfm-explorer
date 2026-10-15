"""
Unit tests for the Shackleton crater context (scripts/shackleton_context.py).
"""

from scripts.shackleton_context import SHACKLETON, CANDIDATE_REGIONS, IAU_GAZETTEER_URL


def test_shackleton_matches_iau_gazetteer():
    """Centre and diameter as given by the IAU Gazetteer, feature 5450."""
    assert SHACKLETON["center_latitude_deg"] == -89.67
    assert SHACKLETON["center_longitude_deg"] == 129.78
    assert SHACKLETON["diameter_km"] == 20.92
    assert SHACKLETON["source"] == IAU_GAZETTEER_URL


def test_candidate_regions_carry_no_unsourced_numbers():
    """Regions are names plus NASA list membership only: no slope, sunlight or safety values."""
    allowed = {"key", "name", "nasa_2022_list", "nasa_2024_list"}
    assert {r["name"] for r in CANDIDATE_REGIONS} == {
        "Connecting Ridge", "Peak Near Shackleton", "Connecting Ridge Extension",
    }
    for r in CANDIDATE_REGIONS:
        assert set(r) == allowed, f"Unexpected fields in {r['name']}: {set(r) - allowed}"
        # All three are in NASA's 2022 list of 13 and absent from the 2024 list of 9.
        assert r["nasa_2022_list"] is True
        assert r["nasa_2024_list"] is False


if __name__ == "__main__":
    test_shackleton_matches_iau_gazetteer()
    test_candidate_regions_carry_no_unsourced_numbers()
    print("All Shackleton context tests passed.")
