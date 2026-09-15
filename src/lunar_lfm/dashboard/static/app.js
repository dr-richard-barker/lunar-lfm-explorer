/**
 * Interactive client controller for NASA-IBM Lunar Foundation Model Explorer.
 * Tablet / iPad touch optimized (ABAI L027).
 */

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

  try {
    const res = await fetch("/api/modalities");
    const data = await res.json();
    renderModalities(data, "ALL");

    // Filter buttons
    document.querySelectorAll(".btn-filter").forEach((btn) => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".btn-filter").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        renderModalities(data, btn.getAttribute("data-family"));
      });
    });
  } catch (err) {
    container.innerHTML = `<p class="text-muted">Error loading modalities: ${err.message}</p>`;
  }
}

function renderModalities(data, familyFilter) {
  const container = document.getElementById("modalities-list");
  container.innerHTML = "";

  if (familyFilter === "CONTEXT") {
    // Render optical metadata & static context
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

    // Calculate shadow offset and elongation based on solar incidence and azimuth
    // Solar incidence: 0 = zenith (no shadow), 89 = grazing (very long shadow)
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

    // Update sunlight direction vector
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
      const totalDenseTokens = 5 * patchesPerMod; // Example 5 WAC dense modalities
      const totalTokens = totalDenseTokens + 8 + 28; // + 8 optical + 28 static context

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

  try {
    const res = await fetch("/api/benchmarks");
    const data = await res.json();

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
  } catch (err) {
    container.innerHTML = `<p class="text-muted">Error loading benchmarks: ${err.message}</p>`;
  }
}

/* Hugging Face Hub Probe */
async function initHubProbe() {
  const container = document.getElementById("hub-status-content");
  const refreshBtn = document.getElementById("btn-refresh-hub");
  if (!container) return;

  async function loadHubStatus() {
    container.innerHTML = `<p class="text-muted">Querying Hugging Face API...</p>`;
    try {
      const res = await fetch("/api/hub-status");
      const data = await res.json();

      if (data.error) {
        container.innerHTML = `
          <div class="info-alert">
            <strong>Status Notice:</strong> ${data.error}<br>
            <span class="text-muted">${data.offline_guidance || ""}</span>
          </div>
        `;
        return;
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
    } catch (err) {
      container.innerHTML = `<p class="text-muted">Network error querying Hugging Face: ${err.message}</p>`;
    }
  }

  refreshBtn?.addEventListener("click", loadHubStatus);
  loadHubStatus();
}
