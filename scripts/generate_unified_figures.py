#!/usr/bin/env python3
"""
generate_unified_figures.py
Generates high-resolution publication figures for the unified Moon & Mars paper.
"""

import os
import csv
import matplotlib.pyplot as plt

def generate_figure1_spectrum():
    csv_path = "data/unified_36_landing_sites.csv"
    if not os.path.exists(csv_path):
        print(f"File {csv_path} not found. Run generate_unified_dataset.py first.")
        return

    sites = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["b_surf_est_nt"] = float(row["b_surf_est_nt"])
            sites.append(row)

    # Sort by magnetic intensity
    sites.sort(key=lambda x: x["b_surf_est_nt"])

    site_names = [s["site"] for s in sites]
    b_values = [s["b_surf_est_nt"] for s in sites]
    colors = ['#1f77b4' if s["target"] == 'Moon' else '#d62728' for s in sites]

    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    bars = ax.barh(site_names, b_values, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)

    ax.set_xscale('log')
    ax.axvline(x=50000, color='forestgreen', linestyle='--', linewidth=1.5, label="Earth Geomagnetic Field (GMF ~ 50,000 nT)")
    ax.axvline(x=5000, color='darkorange', linestyle=':', linewidth=1.5, label="Hypomagnetic Field Threshold (< 5,000 nT)")

    ax.set_xlabel("Surface Magnetic Field Intensity |B_surf| (nT, log scale)")
    ax.set_title("Comparative Magnetic Environment Across 36 Lunar & Martian Landing Sites")
    
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#1f77b4', lw=6, label='Lunar Landing Sites (23 sites)'),
        Line2D([0], [0], color='#d62728', lw=6, label='Martian Landing Sites (13 sites)'),
        Line2D([0], [0], color='forestgreen', lw=1.5, ls='--', label='Earth GMF (~ 50,000 nT)'),
        Line2D([0], [0], color='darkorange', lw=1.5, ls=':', label='Hypomagnetic Threshold (5,000 nT)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', frameon=True, facecolor='white', framealpha=0.9)

    plt.tight_layout()
    os.makedirs("figures", exist_ok=True)
    fig_path = "figures/fig1_landing_sites_combined_spectrum.pdf"
    plt.savefig(fig_path, bbox_inches='tight')
    plt.savefig("figures/fig1_landing_sites_combined_spectrum.png", dpi=300, bbox_inches='tight')
    print(f"Saved Figure 1 to {fig_path}")
    plt.close()

def main():
    generate_figure1_spectrum()

if __name__ == "__main__":
    main()
