# Unified Planetary Magnetobiology of the Moon and Mars

**Comparative Planetary Magnetobiology of the Moon and Mars: Integrated Geophysical Mapping, Hypomagnetic Stress Synthesis, and Operational Life Support Frameworks for Deep-Space Exploration**

## Authors
- **Richard Barker**¹* (rbarker2@purdue.edu)
- **Adriana Kaley Sanchez**¹
- **Manisha Dagar**¹
- **Katrina Boland**¹
- **Cauê Sciascia Borlina**²
- **D. Marshall Porterfield**¹

¹ *Department of Agricultural and Biological Engineering, Purdue University, West Lafayette, IN 47907, USA*  
² *Department of Earth, Atmospheric, and Planetary Sciences, Purdue University, West Lafayette, IN 47907, USA*  

---

## Overview
This repository contains the unified dataset, analysis pipeline, and LaTeX manuscript merging our standalone investigations into the magnetic environments of the Moon and Mars into a single comprehensive investigation.

We analyze the crustal magnetic field across **36 landing sites** (23 Lunar sites, including all 13 Artemis III South Polar candidate landing regions, and 13 Martian sites, including ice-rich human ISRU landing regions, active rovers, and southern anomaly belts). We synthesize these physical determinations with an exhaustive review of terrestrial hypomagnetic field (HMF) literature across plants, micro-organisms, and mammalian physiology.

---

## Repository Structure
```
Lunar_analysis/
├── manuscript/
│   ├── main.tex                             # Primary LaTeX manuscript
│   ├── npj-article.cls                      # npj Microgravity journal class
│   ├── references.bib                       # Merged BibTeX bibliography
│   └── sections/
│       ├── abstract.tex                     # Abstract & keywords
│       ├── introduction.tex                 # Narrative introduction
│       ├── results.tex                      # Quantitative results & 36-site synthesis
│       ├── discussion.tex                   # Discussion & operational recommendations
│       ├── methods.tex                      # Datasets & interpolation methodology
│       └── conclusion.tex                   # Concluding synthesis
├── tables/
│   ├── table1_comparative_landing_sites.tex  # 36-site dataset LaTeX table
│   ├── table2_unified_biology_literature.tex # Magnetobiology literature review LaTeX table
│   └── table3_unified_risk_matrix.tex        # Multi-planetary risk matrix LaTeX table
├── figures/
│   ├── fig1_landing_sites_combined_spectrum.pdf
│   └── fig1_landing_sites_combined_spectrum.png
├── scripts/
│   ├── generate_unified_dataset.py          # Merges 36 landing sites into CSV and LaTeX
│   └── generate_unified_figures.py          # Generates publication figures
├── data/
│   └── unified_36_landing_sites.csv         # Processed CSV dataset
└── Makefile                                 # Build automation
```

---

## Instructions

### 1. Generate Dataset & Tables
```bash
python3 scripts/generate_unified_dataset.py
```

### 2. Generate Publication Figures
```bash
python3 scripts/generate_unified_figures.py
```

### 3. Compile LaTeX Manuscript
```bash
make pdf
# or
cd manuscript && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

---

## License
All code and datasets are open source under the MIT License.
