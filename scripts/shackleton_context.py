#!/usr/bin/env python3
"""
Shackleton crater context for the NASA-IBM LFM explorer.

Records only facts that can be checked against a cited source:

- Shackleton crater centre and diameter from the IAU Gazetteer of Planetary Nomenclature
  (feature 5450).
- Which nearby regions NASA named as Artemis III candidate landing regions: 13 regions in the
  release of 19 Aug 2022; 9 regions in the update of 28 Oct 2024. The three regions near
  Shackleton are in the 2022 list and not in the 2024 list.

It deliberately records no slope, illumination, Earth-visibility, rock-abundance or safety
numbers. The repository holds no data from which to compute them, and the NASA-IBM LFM model
card states the model is "not validated for operational decisions such as landing-site
certification or hazard clearance".

Outputs:
- results/shackleton_context.json
- tables/shackleton_candidate_regions.csv
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent

IAU_GAZETTEER_URL = "https://planetarynames.wr.usgs.gov/Feature/5450"
NASA_2022_URL = (
    "https://www.nasa.gov/news-release/"
    "nasa-identifies-candidate-regions-for-landing-next-americans-on-moon/"
)
NASA_2024_URL = (
    "https://www.nasa.gov/news-release/"
    "nasa-provides-update-on-artemis-iii-moon-landing-regions/"
)
QUICKMAP_SOUTH_POLE_URL = "https://quickmap.lroc.im-ldi.com/?extent=-180,-90,180,-85&proj=10"

# IAU Gazetteer, feature 5450 (planetographic, +East).
SHACKLETON = {
    "feature_name": "Shackleton",
    "center_latitude_deg": -89.67,
    "center_longitude_deg": 129.78,
    "diameter_km": 20.92,
    "source": IAU_GAZETTEER_URL,
    "not_recorded": (
        "Depth, floor temperature and wall slopes are not given here: they need a cited "
        "LOLA/Diviner source before they are stated."
    ),
}

# NASA Artemis III candidate landing regions near Shackleton.
CANDIDATE_REGIONS: List[Dict[str, Any]] = [
    {"key": "CR", "name": "Connecting Ridge", "nasa_2022_list": True, "nasa_2024_list": False},
    {"key": "PNS", "name": "Peak Near Shackleton", "nasa_2022_list": True, "nasa_2024_list": False},
    {"key": "CRE", "name": "Connecting Ridge Extension", "nasa_2022_list": True, "nasa_2024_list": False},
]


def build_context() -> Dict[str, Any]:
    return {
        "crater": SHACKLETON,
        "candidate_regions": CANDIDATE_REGIONS,
        "sources": {
            "nasa_2022_release_13_regions": NASA_2022_URL,
            "nasa_2024_update_9_regions": NASA_2024_URL,
            "lroc_quickmap_south_pole": QUICKMAP_SOUTH_POLE_URL,
        },
        "model_card_disclosure": (
            "Not validated for operational decisions such as landing-site certification "
            "or hazard clearance."
        ),
    }


def main() -> None:
    results_dir = REPO_ROOT / "results"
    tables_dir = REPO_ROOT / "tables"
    results_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    json_path = results_dir / "shackleton_context.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(build_context(), f, indent=2)
        f.write("\n")

    csv_path = tables_dir / "shackleton_candidate_regions.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Region",
            "In NASA Artemis III list, Aug 2022 (13 regions)",
            "In NASA Artemis III list, Oct 2024 (9 regions)",
            "LROC QuickMap",
        ])
        for r in CANDIDATE_REGIONS:
            writer.writerow([
                r["name"],
                "yes" if r["nasa_2022_list"] else "no",
                "yes" if r["nasa_2024_list"] else "no",
                QUICKMAP_SOUTH_POLE_URL,
            ])

    print(f"Wrote {json_path.relative_to(REPO_ROOT)} and {csv_path.relative_to(REPO_ROOT)}")
    print(f"Shackleton centre {abs(SHACKLETON['center_latitude_deg'])}°S, "
          f"{SHACKLETON['center_longitude_deg']}°E; diameter {SHACKLETON['diameter_km']} km (IAU)")


if __name__ == "__main__":
    main()
