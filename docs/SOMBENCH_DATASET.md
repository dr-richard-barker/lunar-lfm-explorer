# SomBench Pretraining & Benchmark Dataset

**SomBench** is the multi-instrument, multi-resolution lunar benchmark dataset used to pretrain and evaluate the NASA-IBM Lunar Foundation Model.

- **Hugging Face Dataset:** [`nasa-ibm-ai4science/Sombench-pretraining-data`](https://huggingface.co/datasets/nasa-ibm-ai4science/Sombench-pretraining-data)
- **Dataset Collection:** [SomBench Collection on Hugging Face](https://huggingface.co/collections/nasa-ibm-ai4science/lunar-fm-ml-ready-benchmark-dataset-sombench)
- **Total Bundles:** ~1,963,722 co-registered lunar tile bundles

---

## 1. Two Spatial Scale Families

SomBench divides tiles into two spatial resolution regimes. A single sample is either WAC- or NAC-centered; the two families are never mixed within a single sample:

| Scale Family | Footprint | Pixel Resolution | Bundles | Primary Instruments |
|---|---|---|---|---|
| **WAC** | 51.2 km × 51.2 km | ~100 m/pixel | 963,609 | LROC WAC, SLDEM2015 |
| **NAC** | 512 m × 512 m | ~1 m/pixel | 1,000,113 | LROC NAC, NAC-Stereo DTM |

---

## 2. The 9 Dense Imagery Modalities

SomBench tiles are $512 \times 512$ px (dataset card); the model's input size is $256 \times 256$ (model card). The dense modalities are:

### WAC Family (51.2 km footprint)
1. `vis` (5 channels): Visible reflectance bands (415 nm, 566 nm, 604 nm, 643 nm, 689 nm) from LROC WAC.
2. `uv` (2 channels): Ultraviolet reflectance bands (321 nm, 360 nm) from LROC WAC.
3. `dtm` (1 channel): Topographic elevation from SLDEM2015 (combined LOLA altimeter and Kaguya Terrain Camera).
4. `slope` (1 channel): Surface slope derived from SLDEM2015.
5. `aspect` (2 channels): Surface azimuth direction stored as $(\sin \theta, \cos \theta)$ pair to eliminate the 0°/360° angular wrap-around artifact.

### NAC Family (512 m footprint)
6. `nac` (1 channel): High-resolution panchromatic imagery (1 m/px anchor) from LROC NAC.
7. `dtm_3m` (1 channel): 3m meter-scale stereo photogrammetric elevation model.
8. `slope_3m` (1 channel): Topographic slope at meter scale.
9. `aspect_3m` (2 channels): High-resolution slope aspect stored as a $(\sin \theta, \cos \theta)$ pair.

---

## 3. Sequence Context Modalities

### Optical Acquisition Metadata (8 Scalar Fields)
The model card lists: solar incidence, emission, phase and azimuth angles; sub-solar and
tile-centre coordinates; and ground sampling distance. Values are binned and stringified before
text tokenization (for example `C_LON=87.25-->87.50`); the released `backbone/config.yaml` allows
at most 10 tokens for this sequence.

### Static-Map Context (28 Footprint Averages)
Footprint-averaged physical measurements from prior lunar orbital missions:
- **LRO Diviner:** `TREG` (nighttime regolith temperature anomaly), `TBOL` (bolometric temperature), `ROCK_ABUND` (rock abundance), `HPAR` (H-parameter: regolith density scale height), `DICE` (ice stability depth).
- **LRO LOLA:** `ROUGHNESS` (roughness at 50 m baseline, 1 km product), `PSR` (permanently shadowed region mask), `AVG_ILLUM` (average illumination over the 18.6-yr precession cycle), `ALBEDO` (1064 nm normal albedo).
- **Mini-RF:** `MINIRF_*` (circular polarization ratio; S-band reflectivity).
- **Kaguya / SELENE:** `MI_*` (Multiband Imager reflectance and mineralogy), `SW_FE` (space-weathering Fe), `SP_MINER` (Spectral Profiler polar mineralogy).
- **LROC WAC:** `nr643` (643 nm normalized reflectance), `TIO2` (TiO₂ abundance), `WAC_*` (other WAC products).
- **GRAIL:** `GRAVITY` (free-air gravity disturbance).
- **Lunar Prospector:** `HYDROGEN` (hydrogen abundance).

Key names follow the model card; descriptions follow the SomBench dataset card. The released
`backbone/config.yaml` allows at most 31 tokens for this sequence.
