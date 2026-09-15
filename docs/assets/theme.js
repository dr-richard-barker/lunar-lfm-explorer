/* ============================================================================
   Barker Lab / CoSE shared theme — behaviour (v0.1 prototype)
   ========================================================================== */
(function(){
  "use strict";
  var LS_OPEN = "barker.map.open", LS_PANEL = "barker.map.panel", LS_THEME = "barker.theme";
  var slug = document.body.getAttribute("data-site-id") || "";
  var LOGO = document.body.getAttribute("data-brand-logo") || "assets/cose-logo.png";
  var BRAND_URL = document.body.getAttribute("data-brand-url") || "https://cosecloud.com/";

  /* ---------- build DOM shell ---------- */
  var toggle = el("button", {class:"map-toggle", "aria-label":"Toggle navigation map",
    "aria-expanded":"false"});
  toggle.innerHTML = '<span class="bars"><span></span></span><span class="lbl">Map</span>';

  /* top-left bar: COSE brand logo + the map toggle + the light/dark toggle */
  var topbar = el("div", {class:"topbar"});
  var brand = el("a", {class:"cose-brand", href:BRAND_URL, target:"_blank",
    rel:"noopener", title:"COSE — cosecloud.com", "aria-label":"COSE — cosecloud.com"});
  brand.appendChild(el("img", {src:LOGO, alt:"COSE"}));
  var SUN = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  var themeBtn = el("button", {class:"cose-theme-btn",
    "aria-label":"Toggle light or dark theme", title:"Toggle light / dark"});
  topbar.appendChild(brand); topbar.appendChild(toggle);

  var HUB = (window.BARKER_SITES && window.BARKER_SITES.hub) || "";
  if(HUB && slug !== "cose-hub"){
    var hubLink = el("a", {class:"cose-hub-btn", href:HUB,
      title:"All projects — COSE hub", "aria-label":"All projects — COSE hub"});
    hubLink.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.2"/><rect x="14" y="3" width="7" height="7" rx="1.2"/><rect x="3" y="14" width="7" height="7" rx="1.2"/><rect x="14" y="14" width="7" height="7" rx="1.2"/></svg>';
    topbar.appendChild(hubLink);
  }
  if(document.body.getAttribute("data-cose-themetoggle") !== "off"){ topbar.appendChild(themeBtn); }

  var bar = el("nav", {class:"sitebar", "aria-label":"Site and document map"});
  var switcher = el("div", {class:"cose-switch", role:"tablist"});
  var tabDoc  = tab("On this page", true);
  var tabSite = tab("All projects", false);
  switcher.appendChild(tabDoc); switcher.appendChild(tabSite);

  var docPanel  = el("div", {class:"cose-panel", id:"panel-doc"});
  var sitePanel = el("div", {class:"cose-panel", id:"panel-site", hidden:""});
  bar.appendChild(switcher); bar.appendChild(docPanel); bar.appendChild(sitePanel);

  var resizeH = el("div", {class:"cose-resize", "aria-hidden":"true", title:"Drag to resize"});
  bar.appendChild(resizeH);

  var scrim = el("div", {class:"map-scrim"});

  var page = el("div", {class:"page"});
  while(document.body.firstChild){ page.appendChild(document.body.firstChild); }
  document.body.appendChild(topbar);
  document.body.appendChild(bar);
  document.body.appendChild(scrim);
  document.body.appendChild(page);

  /* Match rail + toggle to host page background */
  (function(){
    function lum(c){
      var m = c && c.match(/rgba?\(([^)]+)\)/); if(!m) return null;
      var p = m[1].split(",").map(parseFloat);
      if(p.length >= 4 && p[3] === 0) return null;
      return (0.2126*p[0] + 0.7152*p[1] + 0.0722*p[2]) / 255;
    }
    var l = lum(getComputedStyle(document.body).backgroundColor);
    if(l === null) l = lum(getComputedStyle(document.documentElement).backgroundColor);
    if(l === null) l = window.matchMedia("(prefers-color-scheme: dark)").matches ? 0 : 1;
    var cls = l < 0.45 ? "cose-dark" : "cose-light";
    bar.classList.add(cls); topbar.classList.add(cls);
  })();

  /* Document map from <h2> headings */
  var links = [];
  var scope = page.querySelector("main") || page;
  var heads = [].slice.call(scope.querySelectorAll("h2"));
  var docList = el("ul", {class:"docmap"});
  var idx = 0;
  heads.forEach(function(h){
    if(!h.id){ h.id = "sec-" + (++idx); }
    var label = h.textContent.replace(/\s+/g," ").trim();
    var a = el("a", {href:"#"+h.id});
    a.textContent = label;
    a.addEventListener("click", function(){ if(isOverlay()) close(); });
    var li = el("li"); li.appendChild(a); docList.appendChild(li);
    links.push({a:a, sec:h});
  });
  docPanel.appendChild(header4("On this page"));
  docPanel.appendChild(docList);

  /* Site map from registry */
  var reg = window.BARKER_SITES;
  sitePanel.appendChild(header4("All projects"));
  if(reg && reg.groups){
    var sl = el("ul", {class:"sitemap"});
    reg.groups.forEach(function(g){
      var gl = el("li"); var gh = el("div",{class:"cose-group"}); gh.textContent = g.name;
      gl.appendChild(gh); sl.appendChild(gl);
      g.items.forEach(function(it){
        var li = el("li");
        var node = el("a", {href: it.url || "#"});
        if(it.id === slug){ node.className = "cose-current"; }
        node.innerHTML = (it.emoji ? it.emoji + " " : "") + esc(it.title) + (it.desc? "<small>"+esc(it.desc)+"</small>":"");
        li.appendChild(node); sl.appendChild(li);
      });
    });
    sitePanel.appendChild(sl);
  }

  function selectPanel(which){
    var doc = which==="doc";
    tabDoc.setAttribute("aria-selected", doc);
    tabSite.setAttribute("aria-selected", !doc);
    docPanel.hidden = !doc; sitePanel.hidden = doc;
    try{ localStorage.setItem(LS_PANEL, which); }catch(e){}
  }
  tabDoc.addEventListener("click", function(){ selectPanel("doc"); });
  tabSite.addEventListener("click", function(){ selectPanel("site"); });

  function open(){ document.body.classList.add("map-open"); toggle.setAttribute("aria-expanded","true");
    try{ localStorage.setItem(LS_OPEN,"1"); }catch(e){} }
  function close(){ document.body.classList.remove("map-open"); toggle.setAttribute("aria-expanded","false");
    try{ localStorage.setItem(LS_OPEN,"0"); }catch(e){} }
  function isOverlay(){ return window.matchMedia("(max-width:1179px)").matches; }
  toggle.addEventListener("click", function(){
    document.body.classList.contains("map-open") ? close() : open(); });
  scrim.addEventListener("click", close);
  document.addEventListener("keydown", function(e){ if(e.key==="Escape") close(); });

  function effectiveTheme(){
    return document.documentElement.getAttribute("data-theme")
      || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function applyTheme(t){
    document.documentElement.setAttribute("data-theme", t);
    themeBtn.innerHTML = t === "dark" ? SUN : MOON;
    themeBtn.setAttribute("title", t === "dark" ? "Switch to light" : "Switch to dark");
    [bar, topbar].forEach(function(e){
      e.classList.remove("cose-dark","cose-light");
      e.classList.add(t === "dark" ? "cose-dark" : "cose-light");
    });
    try{ localStorage.setItem(LS_THEME, t); }catch(e){}
  }
  themeBtn.addEventListener("click", function(){
    applyTheme(effectiveTheme() === "dark" ? "light" : "dark"); });
  var savedTheme = null;
  try{ savedTheme = localStorage.getItem(LS_THEME); }catch(e){}
  if(savedTheme){ applyTheme(savedTheme); }
  else { themeBtn.innerHTML = effectiveTheme() === "dark" ? SUN : MOON; }

  function el(tag, attrs){ var n=document.createElement(tag);
    if(attrs) for(var k in attrs){ if(k in n && k!=="hidden" && typeof n[k]!=="object"){} n.setAttribute(k, attrs[k]); }
    return n; }
  function tab(text, sel){ var b=el("button",{role:"tab","aria-selected":String(sel)});
    b.textContent=text; return b; }
  function header4(t){ var h=el("h4"); h.textContent=t; h.style.padding="0 20px"; return h; }
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){
    return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }
})();
