/**
 * Interactive client controller for NASA-IBM Lunar Foundation Model GitHub Pages.
 * Works both with a local API backend and as a self-contained static app on GitHub Pages.
 * Tablet / iPad touch optimized (ABAI L027).
 */

// Ground-truth fallback data for standalone static hosting (GitHub Pages)
const STATIC_FALLBACK_DATA = {
  overview: {
    specs: {
      backbone: "ViT-B",
      embed_dim: 768,
      depth: 12,
      heads: 12,
      input_size: [256, 256],
      pretrain_patch_size: [16, 16],
      fsq_levels: [8, 8, 8, 6, 5],
      total_modalities: 11,
      pretrain_steps: 150000,
      pretrain_hardware: "16 x NVIDIA H100",
      sombench_bundles: 1963722,
      approx_params_m: 178.96,
      approx_weight_gb: 0.33
    }
  },
  modalities: {
    dense: [
      { key: "vis", name: "WAC Visible Reflectance", family: "WAC", channels: 5, resolution_m: 100, instrument: "LROC WAC", description: "5 visible reflectance color bands (415, 566, 604, 643, 689 nm)", channel_names: ["band_415nm", "band_566nm", "band_604nm", "band_643nm", "band_689nm"] },
      { key: "uv", name: "WAC Ultraviolet Reflectance", family: "WAC", channels: 2, resolution_m: 500, instrument: "LROC WAC", description: "2 ultraviolet reflectance bands (321, 360 nm)", channel_names: ["band_321nm", "band_360nm"] },
      { key: "dtm", name: "WAC Digital Terrain Model", family: "WAC", channels: 1, resolution_m: 60, instrument: "SLDEM2015", description: "Global digital elevation model from combined LRO LOLA and Kaguya TC", channel_names: ["elevation"] },
      { key: "slope", name: "WAC Terrain Slope", family: "WAC", channels: 1, resolution_m: 60, instrument: "SLDEM2015", description: "Surface topographic slope derived from SLDEM2015", channel_names: ["slope_deg"] },
      { key: "aspect", name: "WAC Terrain Aspect", family: "WAC", channels: 2, resolution_m: 60, instrument: "SLDEM2015", description: "Surface slope azimuth direction stored as sin/cos pair to avoid angular wrap-around", channel_names: ["sin_aspect", "cos_aspect"] },
      { key: "nac", name: "NAC Panchromatic Imagery", family: "NAC", channels: 1, resolution_m: 1, instrument: "LROC NAC", description: "High-resolution panchromatic visible imagery (0.5 to 2.0 m/pixel)", channel_names: ["panchromatic"] },
      { key: "dtm_3m", name: "NAC Stereo DTM", family: "NAC", channels: 1, resolution_m: 3, instrument: "NAC-stereo DTM", description: "High-resolution 3m stereo photogrammetric elevation model", channel_names: ["elevation_3m"] },
      { key: "slope_3m", name: "NAC High-Res Slope", family: "NAC", channels: 1, resolution_m: 3, instrument: "NAC-stereo DTM", description: "Meter-scale topographic slope derived from 3m stereo DTM", channel_names: ["slope_3m_deg"] },
      { key: "aspect_3m", name: "NAC High-Res Aspect", family: "NAC", channels: 2, resolution_m: 3, instrument: "NAC-stereo DTM", description: "Meter-scale slope aspect stored as sin/cos pair to avoid wrap-around", channel_names: ["sin_aspect_3m", "cos_aspect_3m"] }
    ]
  },
  benchmarks: {
    benchmarks: [
      { id: "robbins_craters_50", name: "Robbins Craters (50% Data)", target: "Impact craters on LROC WAC (~100 m/px)", scale: "WAC", metric: "mAP", direction: "maximize", lfm_score: "0.2541 ± 0.0018", lfm_config: "Full Fine-Tuning", baseline_score: "0.2313 ± 0.0027", baseline_name: "SwinV2-B (ImageNet-22k)", random_init: "0.2197 ± 0.0027", takeaway: "High label efficiency: LFM with 50% data matches or exceeds SwinV2-B on 100% data." },
      { id: "robbins_craters_100", name: "Robbins Craters (100% Data)", target: "Impact craters on LROC WAC (~100 m/px)", scale: "WAC", metric: "mAP", direction: "maximize", lfm_score: "0.2581 ± 0.0017", lfm_config: "LoRA (rank 16, α=32)", baseline_score: "0.2420 ± 0.0047", baseline_name: "SwinV2-B (ImageNet-22k)", random_init: "0.2289 ± 0.0037", takeaway: "LoRA fine-tuning outperforms full fine-tuning with narrower seed spread." },
      { id: "nac_craters_meter_scale", name: "NAC Craters (Meter Scale)", target: "Small impact craters on LROC NAC (1 m/px)", scale: "NAC", metric: "mAP", direction: "maximize", lfm_score: "0.1543 ± 0.0098", lfm_config: "LoRA (rank 16, α=32)", baseline_score: "0.1552 ± 0.0086", baseline_name: "SwinV2-B", random_init: "0.1274 ± 0.0151", takeaway: "Leaders are comparable within seed spread; frozen encoder fails at meter scale." },
      { id: "irregular_mare_patches", name: "Irregular Mare Patches (IMP)", target: "Young volcanic surface features / enigmatic mounds", scale: "NAC/WAC", metric: "IoU₁", direction: "maximize", lfm_score: "0.5709 ± 0.0114", lfm_config: "Frozen Encoder", baseline_score: "0.5687 ± 0.0181", baseline_name: "ConvNeXtV2-B", random_init: "0.3142 ± 0.0746", takeaway: "Pretraining is essential: random-init collapses to 0.3142. Frozen encoder yields strongest generalization." },
      { id: "polar_ice_prospectivity", name: "Polar Ice Prospectivity", target: "Permanently Shadowed Regions (PSRs) ice stability", scale: "WAC/Context", metric: "RMSE", direction: "minimize", lfm_score: "0.0293 ± 0.0013", lfm_config: "Full Fine-Tuning", baseline_score: "0.0377 ± 0.0004", baseline_name: "SwinV2-B", random_init: "0.0397 ± 0.0004", takeaway: "Widest margin: 22% RMSE reduction. 3-modality LFM matches full-stack ConvNeXt-B." }
    ],
    disclosures: [
      { category: "Geodetic Reference Frame", statement: "The model maintains NO geodetic reference frame. It captures local topographic shape and relative gradients, but absolute elevation has an offset shift, and generated coordinates can drift by tens of degrees.", severity: "CRITICAL_LIMITATION" },
      { category: "Ice Prospectivity Target", statement: "Ice-prospectivity outputs regress a knowledge-driven fuzzy-overlay prospectivity target, NOT direct in-situ water ice measurements.", severity: "SCIENTIFIC_CAUTION" },
      { category: "Operational Certification", statement: "The model is NOT certified for operational mission decisions such as landing-site certification, terrain hazard clearance, or rover traverse path clearance.", severity: "OPERATIONAL_BOUNDARY" },
      { category: "Cross-Modal Generation", statement: "Any-to-any multimodal reconstructions are qualitative probes of cross-modal latent alignment, NOT calibrated radiometry or photogrammetry.", severity: "METHODOLOGY_NOTE" }
    ]
  },
  hub: {
    id: "nasa-ibm-ai4science/NASA-IBM-Lunar-Foundation-Model",
    downloads: 1948,
    likes: 35,
    usedStorage: 12789820545,
    siblings: [
      { rfilename: "README.md" },
      { rfilename: "NI_LFM_Technical_Report.pdf" },
      { rfilename: "model_scheme.png" },
      { rfilename: "backbone/checkpoint.pt" },
      { rfilename: "backbone/config.yaml" },
      { rfilename: "tokenizers/NAC_aspect3m/checkpoint.pt" },
      { rfilename: "tokenizers/NAC_dtm3m_local/checkpoint.pt" },
      { rfilename: "tokenizers/NAC_nac/checkpoint.pt" },
      { rfilename: "tokenizers/NAC_slope3m/checkpoint.pt" },
      { rfilename: "tokenizers/WAC_aspect/checkpoint.pt" },
      { rfilename: "tokenizers/WAC_dtm/checkpoint.pt" },
      { rfilename: "tokenizers/WAC_slope/checkpoint.pt" },
      { rfilename: "tokenizers/WAC_uv/checkpoint.pt" },
      { rfilename: "tokenizers/WAC_vis/checkpoint.pt" }
    ]
  }
};

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initModalityExplorer();
  initGeometrySimulator();
  initFlexiViTExplorer();
  initBenchmarks();
  initHubProbe();
});

/* Tab Switching */
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach((pane) => {
        pane.classList.remove("active");
      });
      document.getElementById(targetId)?.classList.add("active");
    });
  });
}

/* Modality Explorer */
async function initModalityExplorer() {
  const container = document.getElementById("modalities-list");
  if (!container) return;

  let data = STATIC_FALLBACK_DATA.modalities;
  try {
    const res = await fetch("/api/modalities");
    if (res.ok) {
      data = await res.json();
    }
  } catch (err) {
    // Graceful fallback on static host
  }

  renderModalities(data, "ALL");

  document.querySelectorAll(".btn-filter").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".btn-filter").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      renderModalities(data, btn.getAttribute("data-family"));
    });
  });
}

function renderModalities(data, familyFilter) {
  const container = document.getElementById("modalities-list");
  container.innerHTML = "";

  if (familyFilter === "CONTEXT") {
    const optCard = document.createElement("div");
    optCard.className = "modality-card";
    optCard.innerHTML = `
      <div class="modality-header">
        <span class="modality-tag">CONTEXT SEQUENCE</span>
        <span class="badge badge-accent">8 Fields</span>
      </div>
      <div class="modality-title">Optical Metadata Sequence</div>
      <div class="modality-desc">Illumination geometry and positioning angles passed as explicit token sequences.</div>
      <div class="modality-details">
        <strong>Fields:</strong> solar_incidence, emission_angle, phase_angle, solar_azimuth, subsolar_lat/lon, center_lat/lon.
      </div>
    `;
    container.appendChild(optCard);

    const ctxCard = document.createElement("div");
    ctxCard.className = "modality-card";
    ctxCard.innerHTML = `
      <div class="modality-header">
        <span class="modality-tag">CONTEXT SEQUENCE</span>
        <span class="badge badge-outline">28 Fields</span>
      </div>
      <div class="modality-title">Static-Map Footprint Context</div>
      <div class="modality-desc">Footprint-averaged thermophysics, radar, gravity, mineralogy, and LOLA metrics.</div>
      <div class="modality-details">
        <strong>Instruments:</strong> Diviner (TREG, TBOL, DICE), LOLA (PSR, ROUGHNESS), Mini-RF (CPR), Kaguya (SP, MI), GRAIL, LP.
      </div>
    `;
    container.appendChild(ctxCard);
    return;
  }

  const filtered = data.dense.filter((m) => {
    if (familyFilter === "ALL") return true;
    return m.family === familyFilter;
  });

  filtered.forEach((m) => {
    const card = document.createElement("div");
    card.className = "modality-card";
    const tagClass = m.family === "WAC" ? "badge-outline" : "badge-accent";
    card.innerHTML = `
      <div class="modality-header">
        <span class="modality-tag">${m.family} (${m.resolution_m}m)</span>
        <span class="badge ${tagClass}">${m.channels} Ch</span>
      </div>
      <div class="modality-title">${m.name} (${m.key})</div>
      <div class="modality-desc">${m.description}</div>
      <div class="modality-details">
        <strong>Source:</strong> ${m.instrument} | <strong>Channels:</strong> ${m.channel_names.join(", ")}
      </div>
    `;
    container.appendChild(card);
  });
}

/* Solar Geometry & Shadow Simulator */
function initGeometrySimulator() {
  const incSlider = document.getElementById("solar-incidence");
  const azimSlider = document.getElementById("solar-azimuth");
  const valInc = document.getElementById("val-incidence");
  const valAzim = document.getElementById("val-azimuth");
  const tokenPreview = document.getElementById("geometry-token-preview");
  const shadowElem = document.getElementById("crater-shadow");
  const sunVector = document.getElementById("sun-vector");

  function update() {
    const inc = parseFloat(incSlider.value);
    const azim = parseFloat(azimSlider.value);

    valInc.textContent = `${inc}°`;
    valAzim.textContent = `${azim}°`;

    tokenPreview.textContent = `INC=${inc.toFixed(1)} | AZIM=${azim.toFixed(1)} | EMISS=0.0 | PHASE=${inc.toFixed(1)} | C_LAT=0.00 | C_LON=0.00`;

    const radAzim = (azim * Math.PI) / 180;
    const shadowDist = Math.tan((inc * Math.PI) / 180) * 18;
    const clampedDist = Math.min(shadowDist, 85);

    const shadowX = 150 + Math.cos(radAzim) * clampedDist;
    const shadowY = 150 + Math.sin(radAzim) * clampedDist;

    const rx = 65 + clampedDist * 0.4;
    const ry = 45;

    shadowElem.setAttribute("cx", shadowX.toFixed(1));
    shadowElem.setAttribute("cy", shadowY.toFixed(1));
    shadowElem.setAttribute("rx", rx.toFixed(1));
    shadowElem.setAttribute("ry", ry.toFixed(1));

    const sunStartX = 150 - Math.cos(radAzim) * 110;
    const sunStartY = 150 - Math.sin(radAzim) * 110;
    sunVector.setAttribute("x1", sunStartX.toFixed(1));
    sunVector.setAttribute("y1", sunStartY.toFixed(1));
  }

  incSlider?.addEventListener("input", update);
  azimSlider?.addEventListener("input", update);
  update();
}

/* FlexiViT Patch Explorer */
function initFlexiViTExplorer() {
  const buttons = document.querySelectorAll(".btn-patch");
  const metricGrid = document.getElementById("metric-grid");
  const metricPatches = document.getElementById("metric-patches");
  const metricSeq = document.getElementById("metric-seq");

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const patch = parseInt(btn.getAttribute("data-patch"), 10);
      const gridDim = 256 / patch;
      const patchesPerMod = gridDim * gridDim;
      const totalDenseTokens = 5 * patchesPerMod;
      const totalTokens = totalDenseTokens + 8 + 28;

      metricGrid.textContent = `${gridDim} × ${gridDim}`;
      metricPatches.textContent = patchesPerMod.toLocaleString();
      metricSeq.textContent = totalTokens.toLocaleString();
    });
  });
}

/* SomBench Benchmarks */
async function initBenchmarks() {
  const container = document.getElementById("benchmarks-list");
  const discContainer = document.getElementById("disclosures-list");
  if (!container || !discContainer) return;

  let data = STATIC_FALLBACK_DATA.benchmarks;
  try {
    const res = await fetch("/api/benchmarks");
    if (res.ok) {
      data = await res.json();
    }
  } catch (err) {
    // Graceful fallback
  }

  container.innerHTML = "";
  data.benchmarks.forEach((b) => {
    const card = document.createElement("div");
    card.className = "benchmark-card";
    const dirSym = b.direction === "maximize" ? "↑" : "↓";
    card.innerHTML = `
      <div class="benchmark-title">${b.name}</div>
      <div class="benchmark-metric">Metric: <strong>${b.metric}</strong> (${dirSym}) [${b.scale}]</div>
      <div class="score-bar-container">
        <div class="score-row">
          <span>NASA-IBM LFM (${b.lfm_config}):</span>
          <span class="score-val highlight">${b.lfm_score}</span>
        </div>
        <div class="score-row">
          <span>Best Baseline (${b.baseline_name}):</span>
          <span class="score-val">${b.baseline_score}</span>
        </div>
        <div class="score-row">
          <span>Random-Init Control:</span>
          <span class="score-val">${b.random_init}</span>
        </div>
      </div>
      <div class="benchmark-takeaway">${b.takeaway}</div>
    `;
    container.appendChild(card);
  });

  discContainer.innerHTML = "";
  data.disclosures.forEach((d) => {
    const item = document.createElement("div");
    item.className = `disclosure-item ${d.severity}`;
    item.innerHTML = `
      <h4>[${d.severity}] ${d.category}</h4>
      <p>${d.statement}</p>
    `;
    discContainer.appendChild(item);
  });
}

/* Hugging Face Hub Probe */
async function initHubProbe() {
  const container = document.getElementById("hub-status-content");
  const refreshBtn = document.getElementById("btn-refresh-hub");
  if (!container) return;

  async function loadHubStatus() {
    container.innerHTML = `<p class="text-muted">Querying Hugging Face API...</p>`;
    let data = STATIC_FALLBACK_DATA.hub;
    try {
      const res = await fetch("/api/hub-status");
      if (res.ok) {
        data = await res.json();
      }
    } catch (err) {
      // Graceful fallback to verified static repository record
    }

    const files = data.siblings || [];
    const fileListHtml = files
      .map((f) => `<li>• ${f.rfilename}</li>`)
      .slice(0, 15)
      .join("");

    container.innerHTML = `
      <div class="hub-stat-row">
        <div class="metric-box">
          <span class="metric-val">${(data.downloads || 0).toLocaleString()}</span>
          <span class="metric-lbl">Downloads</span>
        </div>
        <div class="metric-box">
          <span class="metric-val">${data.likes || 0}</span>
          <span class="metric-lbl">Likes</span>
        </div>
        <div class="metric-box">
          <span class="metric-val">${files.length}</span>
          <span class="metric-lbl">Registered Files</span>
        </div>
        <div class="metric-box">
          <span class="metric-val">${(data.usedStorage ? (data.usedStorage / (1024**3)).toFixed(1) + ' GB' : '~12.8 GB')}</span>
          <span class="metric-lbl">Total Checkpoints Size</span>
        </div>
      </div>
      <h3>Registered Repository Sibling Files</h3>
      <ul class="file-list mt-4">${fileListHtml}</ul>
    `;
  }

  refreshBtn?.addEventListener("click", loadHubStatus);
  loadHubStatus();
}
