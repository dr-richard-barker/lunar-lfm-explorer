# NASA-IBM Lunar Foundation Model Explorer (`lunar-lfm-explorer`)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![FAIR Software](https://img.shields.io/badge/FAIR-Compliant-success.svg)](https://fair-software.eu/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Model: Hugging Face](https://img.shields.io/badge/HF_Model-NASA--IBM--Lunar--Foundation--Model-yellow.svg)](https://huggingface.co/nasa-ibm-ai4science/NASA-IBM-Lunar-Foundation-Model)
[![Dataset: SomBench](https://img.shields.io/badge/HF_Dataset-Sombench--pretraining--data-orange.svg)](https://huggingface.co/datasets/nasa-ibm-ai4science/Sombench-pretraining-data)

A **FAIR (Findable, Accessible, Interoperable, Reusable)** scientific toolkit and multi-device interactive explorer for the **NASA-IBM Lunar Foundation Model (NASA-IBM LFM)**.

The model is a multimodal, multi-resolution Vision Transformer (ViT-B) encoder–decoder trained from scratch on **SomBench** (~2 million co-registered lunar tile bundles across 11 modalities at two spatial scales). This repository provides lightweight inspection, modality schemas, acquisition geometry modeling, benchmark ground truth, and an interactive dashboard optimized for both desktop and iPad/touchscreens, designed in accordance with **ABAI (AstroBotany AI)** scientific software standards.

---

## Key Features

1. **Zero-Synthetic Model & Data Inspection (ABAI [[L006]])**
   - Inspect ViT-B configuration (768 dim, 12 layers, 12 heads), parameter counts (~86M encoder), FSQ quantization levels `(8, 8, 8, 6, 5)`, and FlexiViT patch grids instantly without downloading the 12.8 GB model weights.
   - **Zero-Synthetic Guarantee**: Absolute prohibition against silent synthetic fallback (no `np.random` masquerading as real results).
2. **SomBench 11 Modalities System**
   - **WAC Family (51.2 km footprint, ~100 m/px):** Visible (`vis` 5 bands), UV (`uv` 2 bands), Topography (`dtm`), Slope (`slope`), Aspect (`aspect` sin/cos pair).
   - **NAC Family (512 m footprint, ~1 m/px):** Panchromatic (`nac`), Stereo DTM (`dtm_3m`), Slope (`slope_3m`), Aspect (`aspect_3m`).
   - **Context Sequences:** 8 Optical Metadata fields (solar incidence, emission, phase, azimuth angles) and 28 Static-Map context fields (Diviner thermophysics, LOLA roughness/PSR, Mini-RF radar, Kaguya mineralogy, GRAIL, Lunar Prospector).
3. **Interactive Solar Geometry & Shadow Simulator**
   - Dynamic simulation showing how solar incidence and azimuth angles govern lunar surface appearance and how the model sequences acquisition geometry to eliminate illumination confounds.
4. **Multi-Device Interactive Dashboard (ABAI [[L027]])**
   - Pure HTML5/CSS3/JS touch-first explorer with $\ge 44\text{px}$ touch targets, responsive across desktop monitors and iPad/tablet touchscreens.
5. **SomBench Benchmark Ground Truth & Scientific Disclosures (ABAI [[L001]])**
   - Complete reported scores across Robbins craters (WAC), meter-scale NAC craters, Irregular Mare Patches (IMP) segmentation, and Polar Ice Prospectivity.
   - Explicit scientific disclosures regarding geodetic frames, ice prospectivity models, and operational limitations.
6. **FAIR Software Compliance (ABAI [[L025]])**
   - Machine-readable citation (`CITATION.cff`), CodeMeta metadata (`codemeta.json`), Apache-2.0 open-source licensing, and reproducible test suite.

---

## Repository Structure

```
Lunar_analysis/
├── CITATION.cff                        # FAIR citation metadata with grounded citations
├── codemeta.json                       # FAIR software metadata
├── LICENSE                             # Apache-2.0
├── pyproject.toml                      # Modern packaging configuration
├── README.md                           # This documentation
├── STATE.md                            # Resumable task state tracking (ABAI L026/L027)
├── src/
│   └── lunar_lfm/
│       ├── __init__.py                 # Package exports
│       ├── config.py                   # Ground truth specifications & constants
│       ├── modalities.py               # 11 modalities registry & bundle validation
│       ├── model_inspect.py            # ViT-B, FlexiViT & tokenizer inspector
│       ├── benchmarks.py               # SomBench benchmark records & disclosures
│       ├── hub.py                      # Hugging Face client with offline resilience
│       ├── cli.py                      # CLI entry point (`lunar-lfm`)
│       └── dashboard/                  # Interactive touch & desktop web explorer
│           ├── app.py                  # Lightweight local HTTP server
│           └── static/                 # Touch-responsive UI (HTML, CSS, JS, SVG)
├── scripts/
│   ├── run_explorer.py                 # Convenience launcher (CLI or --serve)
│   ├── verify_fair_compliance.py       # Automated FAIR & ABAI landmine auditor
│   └── fetch_sample_metadata.py        # Hugging Face metadata caching utility
├── tests/                              # Pytest test suite with non-vacuous assertions
├── tables/                             # CSV reference tables for modalities & benchmarks
├── results/                            # JSON dataset summaries
├── figures/                            # Vector architecture diagrams (ABAI L018)
└── docs/                               # Architecture, SomBench, and ABAI audit docs
```

---

## Quickstart

### 1. Installation

Clone and install in editable mode:
```bash
git clone https://github.com/dr-richard-barker/Lunar_analysis.git
cd Lunar_analysis
pip install -e .
```

To run tests or developer tools:
```bash
pip install -e ".[dev]"
```

### 2. Command-Line Interface (`lunar-lfm`)

```bash
# Model & training summary
python3 -m lunar_lfm.cli info

# Inspect all 11 SomBench modalities
python3 -m lunar_lfm.cli inspect-modalities

# Filter modalities by scale family (WAC or NAC)
python3 -m lunar_lfm.cli inspect-modalities --family WAC

# Inspect ViT-B architecture and test FlexiViT patch resizing (e.g. ps8, ps16, ps32)
python3 -m lunar_lfm.cli inspect-model --patch-size 8

# Review downstream benchmark performance and official scientific disclosures
python3 -m lunar_lfm.cli benchmarks

# Probe live Hugging Face repository files and checkpoint storage
python3 -m lunar_lfm.cli hub-status

# Run local schema and integrity verification
python3 -m lunar_lfm.cli verify
```

### 3. Launching the Interactive Web Dashboard

Launch the zero-dependency local web dashboard:
```bash
python3 scripts/run_explorer.py --serve --port 8088
```
Open **http://localhost:8088** in your browser or tablet. The interface includes:
- **Modality Explorer**: Toggle between WAC regional imagery, NAC meter-scale terrain, and context sequences.
- **Solar Geometry Simulator**: Interactive sliders for solar incidence (0°–89°) and azimuth (0°–360°) with dynamic SVG crater shadow casting.
- **FlexiViT Patch Grid**: Live calculation of patch grids and multi-modal sequence token lengths.
- **Benchmarks & Disclosures**: Ground-truth bar charts comparing NASA-IBM LFM against SwinV2-B and baseline models.
- **Hub Probe**: Live repository file manifest and storage inspection.

---

## Testing & FAIR Compliance

Run the automated test suite:
```bash
pytest -v tests/
```

Run the automated FAIR and ABAI landmine compliance auditor:
```bash
python3 scripts/verify_fair_compliance.py
```

The compliance script mechanically verifies:
- FAIR metadata files exist and are non-empty
- Zero template-fabricated DOIs exist across all files ([[L003]])
- Zero silent synthetic fallbacks (`np.random`) exist in source code ([[L006]])
- Large model binaries (`*.pt`, `*.safetensors`, ~12.8 GB) are excluded from Git ([[L022]])
- Directory layout matches standard scientific research scaffolding ([[L025]])
- Non-vacuous test assertions pass ([[L008]])

---

## Citations

If you use this toolkit or the underlying model representations, please cite:

```bibtex
@article{fraccaro2026lfm,
  title  = {Multimodal-Multiresolution Foundation Model for Lunar Remote Sensing},
  author = {Fraccaro, Paolo and Nyirjesy, Gabby and Szwarcman, Daniela and Patil, Himanshu
            and Gaur, Vishal and Lal, Rohit and Slank, Rachel A. and Dawson, Geoffrey
            and Debary, Hiyam and Dionelis, Nikolaos and Barker, Michael K. and Annex, Andrew
            and Viswanathan, Vishnu and Morse, Zachary and Schaefer, Ethan I. and Kumar, Ankur
            and Watson, Campbell D. and Dawson-Rigas, Rebekah I. and Maskey, Manil
            and Roy, Sujit and Ramachandran, Rahul and Bernab{\'e}-Moreno, Juan},
  year   = {2026},
  url    = {https://huggingface.co/nasa-ibm-ai4science/NASA-IBM-Lunar-Foundation-Model/blob/main/NI_LFM_Technical_Report.pdf}
}

@misc{sombench2026collection,
  author       = {Patil, Himanshu and Nyirjesy, Gabby and Slank, Rachel A. and Gaur, Vishal
                  and Szwarcman, Daniela and Fraccaro, Paolo and Dionelis, Nikolaos and Barker, Michael K.
                  and Annex, Andrew and Viswanathan, Vishnu and Morse, Zachary and Schaefer, Ethan I.
                  and Debary, Hiyam and Kumar, Ankur and Lal, Rohit and Dawson, Geoffrey
                  and Watson, Campbell and Dawson-Rigas, Rebekah I. and Maskey, Manil
                  and Bernab{\'e}-Moreno, Juan and Ramachandran, Rahul and Roy, Sujit},
  title        = {{SomBench}: Benchmark Dataset for Advancing Machine Learning in Lunar Science},
  year         = {2026},
  howpublished = {\url{https://huggingface.co/collections/nasa-ibm-ai4science/lunar-fm-ml-ready-benchmark-dataset-sombench}}
}
```

---

## License

This software is released under the **Apache-2.0 License**. See [LICENSE](LICENSE) for details.
Documentation and reference data are licensed under **CC-BY-4.0**.
