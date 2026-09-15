#!/usr/bin/env node
/**
 * Automated end-to-end DOM test for 3D Multi-Angle Solar Lab buttons and controls.
 * Verifies that all 12 buttons (6 illumination angles + 5 camera presets + 1 auto-rotate toggle)
 * respond to clicks and execute state changes without errors.
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT_DIR, 'docs', 'index.html'), 'utf-8');
const appJs = fs.readFileSync(path.join(ROOT_DIR, 'docs', 'app.js'), 'utf-8');

function makeElement(tag, id = '') {
  return {
    tagName: tag,
    id,
    textContent: '',
    value: '',
    src: '',
    style: {},
    classList: {
      classes: [],
      add(c) { if (!this.classes.includes(c)) this.classes.push(c); },
      remove(c) { this.classes = this.classes.filter(x => x !== c); },
      contains(c) { return this.classes.includes(c); }
    },
    attributes: {},
    setAttribute(k, v) { this.attributes[k] = String(v); },
    getAttribute(k) { return this.attributes[k] !== undefined ? this.attributes[k] : null; },
    removeAttribute(k) { delete this.attributes[k]; },
    hasAttribute(k) { return k in this.attributes; },
    listeners: {},
    addEventListener(ev, cb) {
      if (!this.listeners[ev]) this.listeners[ev] = [];
      this.listeners[ev].push(cb);
    },
    click() {
      if (this.listeners['click']) {
        this.listeners['click'].forEach(cb => cb({ target: this }));
      }
    }
  };
}

// Build mock document
const document = {
  elements: {},
  getElementById(id) {
    if (!this.elements[id]) {
      this.elements[id] = makeElement('div', id);
    }
    return this.elements[id];
  },
  querySelectorAll(sel) {
    return this.queryList[sel] || [];
  },
  queryList: {},
  addEventListener(ev, cb) {
    if (ev === 'DOMContentLoaded') this.domLoaded = cb;
  }
};
global.document = document;
global.window = {
  dispatchEvent: () => {}
};

// Parse angle buttons from HTML
const angleButtons = [];
const angleMatches = [...html.matchAll(/<button[^>]+class=[\"'][^\"']*btn-lab-angle[^\"']*[\"'][^>]*>(.*?)<\/button>/g)];
for (const match of angleMatches) {
  const full = match[0];
  const text = match[1];
  const btn = makeElement('button');
  btn.textContent = text;
  if (full.includes('active')) btn.classList.add('active');
  for (const am of full.matchAll(/([a-z\-]+)=\"([^\"]+)\"/g)) {
    btn.attributes[am[1]] = am[2];
  }
  angleButtons.push(btn);
}
document.queryList['#lab-3d-angle-buttons .btn-lab-angle'] = angleButtons;

// Parse camera preset buttons from HTML
const camPresetButtons = [];
const camMatches = [...html.matchAll(/<button[^>]+class=[\"'][^\"']*btn-cam-preset[^\"']*[\"'][^>]*>(.*?)<\/button>/g)];
for (const match of camMatches) {
  const full = match[0];
  const text = match[1];
  const btn = makeElement('button');
  btn.textContent = text;
  if (full.includes('id=\"lab-btn-autorotate\"')) {
    btn.id = 'lab-btn-autorotate';
    document.elements['lab-btn-autorotate'] = btn;
  }
  if (full.includes('active')) btn.classList.add('active');
  for (const am of full.matchAll(/([a-z\-]+)=\"([^\"]+)\"/g)) {
    btn.attributes[am[1]] = am[2];
  }
  camPresetButtons.push(btn);
}

document.queryList['.cam-presets-bar .btn-cam-preset:not(#lab-btn-autorotate)'] =
  camPresetButtons.filter(b => b.id !== 'lab-btn-autorotate');

// Create model-viewer mock
const mv = makeElement('model-viewer', 'lab-3d-model-viewer');
mv.setAttribute('auto-rotate', '');
mv.autoRotate = true;
document.elements['lab-3d-model-viewer'] = mv;

// Eval client controller
eval(appJs);

// Initialize 3D lab
init3DSolarLab();

console.log('=' .repeat(65));
console.log('  Testing 3D Multi-Angle Solar Lab Buttons & Controls');
console.log('=' .repeat(65));

// 1. Test all 6 illumination angle buttons
console.log('\n[1/3] Testing Illumination Angle Buttons (6 total)...');
assert(angleButtons.length === 6, 'Expected 6 angle buttons');

angleButtons.forEach((btn, idx) => {
  btn.click();
  const expectedModel = 'assets/3d/' + btn.getAttribute('data-model');
  const expectedRegime = btn.getAttribute('data-regime');
  const expectedTile = 'assets/blender_renders/' + btn.getAttribute('data-tile');

  assert(mv.getAttribute('src') === expectedModel, `Mismatch src on button ${idx+1}`);
  assert(mv.src === expectedModel, `Mismatch mv.src on button ${idx+1}`);
  assert(document.getElementById('lab-regime-title').textContent === expectedRegime, `Mismatch title on button ${idx+1}`);
  assert(document.getElementById('lab-tile-preview-img').src === expectedTile, `Mismatch tile src on button ${idx+1}`);

  console.log(`  ✓ Button ${idx+1}: [${btn.textContent}] -> Loaded: ${expectedModel}`);
});

// 2. Test all 5 camera presets and smart auto-rotate stabilization
console.log('\n[2/3] Testing Camera Preset Buttons & Smart Stabilization (5 total)...');
const featurePresets = camPresetButtons.filter(b => b.id !== 'lab-btn-autorotate');
assert(featurePresets.length === 5, 'Expected 5 camera presets');

featurePresets.forEach((btn, idx) => {
  btn.click();
  const expectedOrbit = btn.getAttribute('data-orbit');
  const expectedTarget = btn.getAttribute('data-target');
  const autoBtn = document.getElementById('lab-btn-autorotate');

  assert(mv.getAttribute('camera-orbit') === expectedOrbit, `Mismatch orbit on preset ${idx+1}`);
  assert(mv.getAttribute('camera-target') === expectedTarget, `Mismatch target on preset ${idx+1}`);

  if (btn.textContent.includes('Overview Orbit')) {
    assert(mv.hasAttribute('auto-rotate'), 'Expected auto-rotate active on Overview Orbit');
    assert(autoBtn.textContent.includes('ON'), 'Expected auto-rotate button ON');
  } else {
    assert(!mv.hasAttribute('auto-rotate'), 'Expected auto-rotate paused on feature preset');
    assert(autoBtn.textContent.includes('OFF'), 'Expected auto-rotate button OFF');
  }

  console.log(`  ✓ Preset ${idx+1}: [${btn.textContent}] -> Orbit: ${expectedOrbit}, Target: ${expectedTarget}`);
});

// 3. Test Auto-Rotate toggle button
console.log('\n[3/3] Testing Auto-Rotate Toggle Button (#lab-btn-autorotate)...');
const autoBtn = document.getElementById('lab-btn-autorotate');
assert(autoBtn, 'Missing #lab-btn-autorotate element');

// Current state is OFF from previous preset click
assert(!mv.hasAttribute('auto-rotate'), 'Initial state before toggle');
autoBtn.click();
assert(mv.hasAttribute('auto-rotate'), 'State after toggle 1 (should be ON)');
assert(autoBtn.textContent.includes('ON'), 'Button text after toggle 1');
console.log('  ✓ Toggle to ON: ' + autoBtn.textContent);

autoBtn.click();
assert(!mv.hasAttribute('auto-rotate'), 'State after toggle 2 (should be OFF)');
assert(autoBtn.textContent.includes('OFF'), 'Button text after toggle 2');
console.log('  ✓ Toggle to OFF: ' + autoBtn.textContent);

function assert(condition, message) {
  if (!condition) {
    console.error('FAIL:', message);
    process.exit(1);
  }
}

console.log('\n' + '=' .repeat(65));
console.log('  🎉 ALL 12 BUTTONS AND CONTROLS PASSED DOM VERIFICATION!');
console.log('=' .repeat(65));
