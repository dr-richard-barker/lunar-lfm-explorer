#!/usr/bin/env python3
"""
generate_unified_dataset.py
Generates unified dataset CSV and LaTeX tables for the 36 Moon & Mars landing sites.
Uses zero non-standard dependencies (built-in csv module).
"""

import os
import csv

def get_lunar_sites():
    return [
        {"site": "Faustini Rim A", "target": "Moon", "mission": "Artemis III", "lat": -85.30, "lon": 77.00, "b_orb_nt": 0.45, "b_surf_est_nt": 0.45, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Peak Near Shackleton", "target": "Moon", "mission": "Artemis III", "lat": -89.70, "lon": 166.00, "b_orb_nt": 0.82, "b_surf_est_nt": 0.82, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Connecting Ridge", "target": "Moon", "mission": "Artemis III", "lat": -88.00, "lon": 137.00, "b_orb_nt": 0.60, "b_surf_est_nt": 0.60, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Connecting Ridge Ext.", "target": "Moon", "mission": "Artemis III", "lat": -88.30, "lon": 148.00, "b_orb_nt": 0.65, "b_surf_est_nt": 0.65, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "de Gerlache Rim 1", "target": "Moon", "mission": "Artemis III", "lat": -88.50, "lon": 290.00, "b_orb_nt": 0.50, "b_surf_est_nt": 0.50, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "de Gerlache Rim 2", "target": "Moon", "mission": "Artemis III", "lat": -88.70, "lon": 294.00, "b_orb_nt": 0.48, "b_surf_est_nt": 0.48, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "de Gerlache-Kocher Massif", "target": "Moon", "mission": "Artemis III", "lat": -86.00, "lon": 285.00, "b_orb_nt": 0.52, "b_surf_est_nt": 0.52, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Haworth", "target": "Moon", "mission": "Artemis III", "lat": -87.40, "lon": 358.00, "b_orb_nt": 0.40, "b_surf_est_nt": 0.40, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Malapert Massif", "target": "Moon", "mission": "Artemis III", "lat": -86.00, "lon": 0.00, "b_orb_nt": 0.55, "b_surf_est_nt": 0.55, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Leibnitz Beta Plateau", "target": "Moon", "mission": "Artemis III", "lat": -85.00, "lon": 31.00, "b_orb_nt": 0.70, "b_surf_est_nt": 0.70, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Nobile Rim 1", "target": "Moon", "mission": "Artemis III", "lat": -85.40, "lon": 35.00, "b_orb_nt": 0.62, "b_surf_est_nt": 0.62, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Nobile Rim 2", "target": "Moon", "mission": "Artemis III", "lat": -84.80, "lon": 47.00, "b_orb_nt": 0.58, "b_surf_est_nt": 0.58, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Amundsen Rim", "target": "Moon", "mission": "Artemis III", "lat": -84.50, "lon": 85.00, "b_orb_nt": 0.65, "b_surf_est_nt": 0.65, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
        {"site": "Apollo 11", "target": "Moon", "mission": "Apollo", "lat": 0.67, "lon": 23.47, "b_orb_nt": 0.93, "b_surf_est_nt": 0.93, "class": "Low/Null-Field", "source": "Hood et al. (2020)"},
        {"site": "Apollo 12", "target": "Moon", "mission": "Apollo", "lat": -3.01, "lon": 336.58, "b_orb_nt": 1.00, "b_surf_est_nt": 1.00, "class": "Low/Null-Field", "source": "Hood et al. (2020)"},
        {"site": "Apollo 14", "target": "Moon", "mission": "Apollo", "lat": -3.65, "lon": 342.53, "b_orb_nt": 0.44, "b_surf_est_nt": 0.44, "class": "Low/Null-Field", "source": "Hood et al. (2020)"},
        {"site": "Apollo 15", "target": "Moon", "mission": "Apollo", "lat": 26.13, "lon": 3.63, "b_orb_nt": 0.23, "b_surf_est_nt": 0.23, "class": "Low/Null-Field", "source": "Hood et al. (2020)"},
        {"site": "Apollo 16 (Highlands)", "target": "Moon", "mission": "Apollo", "lat": -8.97, "lon": 15.50, "b_orb_nt": 4.94, "b_surf_est_nt": 4.94, "class": "Moderate-Field", "source": "Hood et al. (2020)"},
        {"site": "Apollo 17", "target": "Moon", "mission": "Apollo", "lat": 20.19, "lon": 30.77, "b_orb_nt": 1.08, "b_surf_est_nt": 1.08, "class": "Moderate-Field", "source": "Hood et al. (2020)"},
        {"site": "Chang'e 3", "target": "Moon", "mission": "Chang'e", "lat": 44.12, "lon": 340.49, "b_orb_nt": 0.19, "b_surf_est_nt": 0.19, "class": "Low/Null-Field", "source": "Hood et al. (2020)"},
        {"site": "Chang'e 4 (SPA Basin)", "target": "Moon", "mission": "Chang'e", "lat": -45.46, "lon": 177.60, "b_orb_nt": 0.72, "b_surf_est_nt": 0.72, "class": "Low/Null-Field", "source": "Hood et al. (2020)"},
        {"site": "Chang'e 5", "target": "Moon", "mission": "Chang'e", "lat": 43.06, "lon": 308.08, "b_orb_nt": 0.10, "b_surf_est_nt": 0.10, "class": "Low/Null-Field", "source": "Hood et al. (2020)"},
        {"site": "Chandrayaan-3", "target": "Moon", "mission": "Chandrayaan", "lat": -69.37, "lon": 32.35, "b_orb_nt": 0.78, "b_surf_est_nt": 0.78, "class": "Low/Null-Field", "source": "Hood et al. (2022)"},
    ]

def get_mars_sites():
    return [
        {"site": "Jezero Crater (Perseverance)", "target": "Mars", "mission": "Mars 2020", "lat": 18.45, "lon": 77.45, "b_orb_nt": 2.75, "b_surf_est_nt": 23.40, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Gale Crater (Curiosity)", "target": "Mars", "mission": "MSL", "lat": -4.59, "lon": 137.44, "b_orb_nt": 3.18, "b_surf_est_nt": 27.00, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Elysium Planitia (InSight)", "target": "Mars", "mission": "InSight", "lat": 4.50, "lon": 135.62, "b_orb_nt": 1.99, "b_surf_est_nt": 2013.00, "class": "High-Field Outpost", "source": "Johnson et al. (2020)"},
        {"site": "Meridiani Planum (Opportunity)", "target": "Mars", "mission": "MER-B", "lat": -1.95, "lon": 354.47, "b_orb_nt": 2.55, "b_surf_est_nt": 21.60, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Gusev Crater (Spirit)", "target": "Mars", "mission": "MER-A", "lat": -14.57, "lon": 175.47, "b_orb_nt": 9.08, "b_surf_est_nt": 77.20, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Vastitas Borealis (Phoenix)", "target": "Mars", "mission": "Scout", "lat": 68.22, "lon": 234.25, "b_orb_nt": 0.48, "b_surf_est_nt": 4.10, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Chryse Planitia (Viking 1)", "target": "Mars", "mission": "Viking", "lat": 22.48, "lon": 312.05, "b_orb_nt": 0.59, "b_surf_est_nt": 5.00, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Utopia Planitia (Viking 2)", "target": "Mars", "mission": "Viking", "lat": 47.97, "lon": 134.28, "b_orb_nt": 0.39, "b_surf_est_nt": 3.30, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Utopia Planitia (Zhurong)", "target": "Mars", "mission": "Tianwen-1", "lat": 25.07, "lon": 109.92, "b_orb_nt": 0.76, "b_surf_est_nt": 6.50, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Oxia Planum (ExoMars)", "target": "Mars", "mission": "Rosalind Franklin", "lat": 18.27, "lon": 335.37, "b_orb_nt": 1.82, "b_surf_est_nt": 15.50, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Arcadia Planitia (Human Candidate)", "target": "Mars", "mission": "Human ISRU Base", "lat": 39.30, "lon": 189.70, "b_orb_nt": 0.71, "b_surf_est_nt": 6.00, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Deuteronilus Mensae (Candidate)", "target": "Mars", "mission": "Human ISRU Base", "lat": 39.10, "lon": 23.20, "b_orb_nt": 0.70, "b_surf_est_nt": 5.90, "class": "Low/Null-Field", "source": "Langlais et al. (2019)"},
        {"site": "Terra Sirenum Anomaly Belt", "target": "Mars", "mission": "Science Outpost", "lat": -30.00, "lon": 195.00, "b_orb_nt": 140.07, "b_surf_est_nt": 1190.60, "class": "High-Field Outpost", "source": "Langlais et al. (2019)"},
    ]

def main():
    os.makedirs("tables", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    lunar_sites = get_lunar_sites()
    mars_sites = get_mars_sites()
    all_sites = lunar_sites + mars_sites
    
    csv_path = "data/unified_36_landing_sites.csv"
    fieldnames = ["site", "target", "mission", "lat", "lon", "b_orb_nt", "b_surf_est_nt", "class", "source"]
    
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_sites)
    print(f"Saved dataset CSV to {csv_path}")
    
    # Generate Table 1 LaTeX
    latex_table = """\\begin{table*}[t]
\\centering
\\footnotesize
\\caption{\\textbf{Comparative magnetic field environment across 36 lunar and Martian landing sites.} Magnetic field magnitude at orbital mapping altitude ($|\\mathbf{B}_{\\text{orb}}|$: 30\\,km for Moon, 400\\,km for Mars) and estimated/measured ground surface intensity ($|\\mathbf{B}_{\\text{surf}}|$) derived from satellite magnetometry (Lunar Prospector, Kaguya, MGS, MAVEN) and InSight ground truth \\citep{Hood2020, Hood2022, Langlais2019, Johnson2020}.}
\\label{tab:comparative_landing_sites}
\\begin{tabular}{llrrcll}
\\toprule
\\textbf{Landing Site / Target} & \\textbf{Body / Mission} & \\textbf{Lat ($^\\circ$)} & \\textbf{Lon ($^\\circ$E)} & \\textbf{$|\\mathbf{B}_{\\text{orb}}|$ (nT)} & \\textbf{$|\\mathbf{B}_{\\text{surf}}|$ (nT)} & \\textbf{Classification} \\\\
\\midrule
\\multicolumn{7}{l}{\\textbf{\\textit{Lunar Landing Sites (30\\,km Altitude Baseline)}}} \\\\
"""
    for site in lunar_sites:
        latex_table += f"{site['site']} & {site['target']} / {site['mission']} & {site['lat']:.2f} & {site['lon']:.2f} & {site['b_orb_nt']:.2f} & {site['b_surf_est_nt']:.2f} & {site['class'].lower()} \\\\\n"
        
    latex_table += "\\midrule\n\\multicolumn{7}{l}{\\textbf{\\textit{Martian Landing Sites (400\\,km Altitude Baseline \\& Surface Modeling)}}} \\\\\n"
    for site in mars_sites:
        latex_table += f"{site['site']} & {site['target']} / {site['mission']} & {site['lat']:.2f} & {site['lon']:.2f} & {site['b_orb_nt']:.2f} & {site['b_surf_est_nt']:.1f} & {site['class'].lower()} \\\\\n"
        
    latex_table += """\\bottomrule
\\end{tabular}
\\end{table*}
"""
    
    tex_path = "tables/table1_comparative_landing_sites.tex"
    with open(tex_path, "w") as f:
        f.write(latex_table)
    print(f"Saved Table 1 LaTeX to {tex_path}")

if __name__ == "__main__":
    main()
