# ABAI Lessons Learned Compliance Record

This document records how `lunar-lfm-explorer` directly incorporates the lessons learned, landmines, and standards codified in the **ABAI (AstroBotany AI)** knowledge base (`/Users/drb_laptop/Documents/abai`).

---

## Lesson Audit Matrix

| ABAI Lesson | Title / Landmine | How Addressed in `lunar-lfm-explorer` | Status |
|---|---|---|---|
| **[[L001]]** | Never assert what you have not checked | All architecture parameters (ViT-B 768/12/12, 11 modalities, 2M bundles) and benchmark scores are drawn directly from the official model card and technical report. Unverified claims are prohibited. | **Enforced** |
| **[[L002]]** | Resolve citations and DOIs before writing | `CITATION.cff` and `codemeta.json` cite Fraccaro et al. (2026) and Patil et al. (2026) without fabricated DOIs or hallucinated citations. | **Enforced** |
| **[[L003]]** | Fabricated npj DOI landmine | Automated static analysis in `scripts/verify_fair_compliance.py` and `tests/test_abai_compliance.py` checks all repository files for template-generated fake DOIs. | **Enforced** |
| **[[L006]]** | Silent synthetic fallback publishes random data as results | Absolute prohibition on silent fallback to `np.random` or simulated placeholder data. If weights are missing or offline, the tool reports exact diagnostics rather than faking predictions. | **Enforced** |
| **[[L008]]** | Verify the checker is not vacuously passing | Unit test `test_abai_l008_non_vacuous_assertion_behavior` deliberately supplies malformed schemas and asserts that the validator produces explicit failures. | **Enforced** |
| **[[L013]] / [[L024]]** | Check portfolio ground truth before building | Audited 153 repos in `portfolio.json`. Confirmed prior art in lunar biological growth (`LunarFarm-BLSS`) and leaf CFD (`LunarLeaf-CFD`), and confirmed that a foundation model exploration tool is **genuinely new**. | **Enforced** |
| **[[L016]] / [[L027]]** | Responsive layout & iPad touch support | Interactive dashboard uses responsive grid and minimum touch targets of 44px, tested for both desktop monitors and tablet/iPad touchscreens. | **Enforced** |
| **[[L018]]** | SVG `var()` presentation attributes invisible in WebKit | Vector diagrams in `figures/model_scheme.svg` and `index.html` use direct hex/rgb values instead of CSS `var()` within SVG presentation attributes. | **Enforced** |
| **[[L022]]** | Save code in GitHub, push weights to Zenodo / Hub | Large model binaries (`*.pt`, `*.safetensors`, ~12.8 GB total) are strictly ignored in `.gitignore` and cached outside Git in `~/.cache/lunar_lfm/`. | **Enforced** |
| **[[L025]]** | Standard research-repo scaffold | Repo populated with `src/`, `scripts/`, `results/`, `figures/`, `tables/`, `tests/`, `docs/`, `CITATION.cff`, `codemeta.json`, and `LICENSE`. | **Enforced** |
| **[[L026]]** | Leave resumable state on disk | Project progress and active goals tracked in `STATE.md`. Hub downloads and scans use atomic file writes with `.tmp` staging. | **Enforced** |
| **[[L028]]** | Secrets get pasted into chat | No hardcoded API tokens or credentials in any file. Hub operations operate via public Hugging Face endpoints. | **Enforced** |

---

## Automated Verification

Run the automated compliance checker anytime:
```bash
python3 scripts/verify_fair_compliance.py
```
Or run the unit test suite:
```bash
pytest -v tests/test_abai_compliance.py
```
