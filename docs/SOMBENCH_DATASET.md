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

Each dense modality is a $256 \times 256$ raster image tile:

### WAC Family (51.2 km footprint)
1. `vis` (5 channels): Visible reflectance bands (415 nm, 566 nm, 604 nm, 643 nm, 689 nm) from LROC WAC.
2. `uv` (2 channels): Ultraviolet reflectance bands (321 nm, 360 nm) from LROC WAC.
3. `dtm` (1 channel): Topographic elevation from SLDEM2015 (combined LOLA altimeter and Kaguya Terrain Camera).
4. `slope` (1 channel): Surface slope derived from SLDEM2015.
5. `aspect` (2 channels): Surface azimuth direction stored as $(\sin \theta, \cos \theta)$ pair to eliminate the 0°/360° angular wrap-around artifact.

### NAC Family (512 m footprint)
6. `nac` (1 channel): High-resolution panchromatic visible imagery (0.5 to 2.0 m/px) from LROC NAC.
7. `dtm_3m` (1 channel): 3m meter-scale stereo photogrammetric elevation model.
8. `slope_3m` (1 channel): Topographic slope at meter scale.
9. `aspect_3m` (2 channels): High-resolution slope aspect stored as a $(\sin \theta, \cos \theta)$ pair.

---

## 3. Sequence Context Modalities

### Optical Acquisition Metadata (8 Scalar Fields)
Passed as sequence tokens to capture the exact illumination geometry during exposure:
- `solar_incidence`: Sun angle relative to local surface normal (dominates shadow length)
- `emission_angle`: Spacecraft line-of-sight viewing angle
- `phase_angle`: Angle between illumination source and viewer
- `solar_azimuth`: Azimuth direction of illumination
- `subsolar_lat` / `subsolar_lon`: Subsolar point coordinates
- `center_lat` / `center_lon`: Tile center coordinates

### Static-Map Context (28 Footprint Averages)
Footprint-averaged physical measurements from prior lunar orbital missions:
- **LRO Diviner (Thermophysics):** `TREG` (regolith temperature), `TBOL` (bolometric temperature), `ROCK_ABUND` (rock abundance fraction), `HPAR` (thermal skin depth), `DICE` (depth to ice stability).
- **LRO LOLA (Altimetry & Roughness):** `ROUGHNESS` (kilometer-scale roughness), `PSR` (Permanently Shadowed Region coverage), `AVG_ILLUM` (annual average solar illumination), `ALBEDO` (normal albedo at 1064 nm).
- **Mini-RF (Synthetic Aperture Radar):** `MINIRF_CPR` (Circular Polarization Ratio), `MINIRF_S1`, `MINIRF_DOP`.
- **Kaguya / SELENE (Mineralogy):** `MI_MINERAL`, `SW_FE` (estimated FeO wt%), `SP_MINER`.
- **LROC WAC (Composition):** `nr643`, `TIO2` (estimated TiO2 abundance), `WAC_MATURITY`.
- **GRAIL (Gravity):** `GRAVITY` (Bouguer gravity anomaly).
- **Lunar Prospector (Neutrons):** `HYDROGEN` (epithermal neutron flux).
