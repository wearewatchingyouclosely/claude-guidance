// Appearance for generated HTML pages: style (modern | win95) and theme (system | light | dark), remembered per
// browser in localStorage, plus the small right-click menu and toast the style guide asks for. No dependencies.
// Inline this file into the generated page. Change STORE_KEY per app, so two tools don't share settings.
(function () {
  const STORE_KEY = "myapp:ui";
  const UI = { style: "modern", theme: "system" };
  try { Object.assign(UI, JSON.parse(localStorage.getItem(STORE_KEY) || "{}")); } catch (e) { /* private window: defaults */ }
  // ?style=win95&theme=dark in the URL overrides the saved choice for this visit (links, screenshots, tests).
  const q = new URLSearchParams(location.search);
  if (/^(modern|win95)$/.test(q.get("style") || "")) UI.style = q.get("style");
  if (/^(system|light|dark)$/.test(q.get("theme") || "")) UI.theme = q.get("theme");

  function apply() {
    const r = document.documentElement;
    if (UI.theme === "system") delete r.dataset.theme; else r.dataset.theme = UI.theme;
    if (UI.style === "win95") r.dataset.style = "win95"; else delete r.dataset.style;
    document.dispatchEvent(new CustomEvent("appearance", { detail: { ...UI } }));
  }
  function save() { try { localStorage.setItem(STORE_KEY, JSON.stringify(UI)); } catch (e) { /* not worth an error */ } }
  function set(key, value) { UI[key] = value; save(); apply(); }
  apply(); // run in <head> or at the top of <body> so the page never flashes the wrong style

  // ------------------------------------------------------------ right-click menu
  // items: [{t:"Label", ic:"📋", k:"Ctrl+C", chk:bool, dis:bool, on:fn, sub:[...]}, "-" (separator), ...]
  let menu = null;
  function closeMenu() { if (menu) { menu.remove(); menu = null; } }
  function ctxMenu(x, y, items) {
    closeMenu();
    menu = document.createElement("div");
    menu.className = "ctx";
    for (const it of items) {
      if (it === "-") { const s = document.createElement("div"); s.className = "sep"; menu.appendChild(s); continue; }
      const row = document.createElement("div");
      row.className = "it" + (it.dis ? " dis" : "");
      row.innerHTML = `<span class="ic">${it.chk ? "✓" : (it.ic || "")}</span><span class="tx"></span>` +
        (it.k ? `<span class="k">${it.k}</span>` : "") + (it.sub ? `<span class="k">▸</span>` : "");
      row.querySelector(".tx").textContent = it.t;
      row.onmouseenter = () => { menu.querySelectorAll(".it.act").forEach(e => e.classList.remove("act")); row.classList.add("act"); };
      row.onclick = ev => {
        ev.stopPropagation();
        if (it.dis) return;
        if (it.sub) { const b = row.getBoundingClientRect(); const keep = menu; menu = null; ctxMenu(b.right, b.top, it.sub); keep.remove(); return; }
        closeMenu(); it.on && it.on();
      };
      menu.appendChild(row);
    }
    document.body.appendChild(menu);
    const b = menu.getBoundingClientRect();
    menu.style.left = Math.max(4, Math.min(x, innerWidth - b.width - 4)) + "px";
    menu.style.top = Math.max(4, Math.min(y, innerHeight - b.height - 4)) + "px";
  }
  addEventListener("pointerdown", e => { if (menu && !menu.contains(e.target)) closeMenu(); });
  addEventListener("keydown", e => { if (e.key === "Escape") closeMenu(); });
  addEventListener("blur", closeMenu);

  // Every menu ends with Appearance.
  function appearanceItems() {
    return [{ t: "Appearance", ic: "🎨", sub: [
      { t: "Modern", chk: UI.style !== "win95", on: () => set("style", "modern") },
      { t: "Windows 95", chk: UI.style === "win95", on: () => set("style", "win95") },
      "-",
      ...["system", "light", "dark"].map(th => ({
        t: { system: "System theme", light: "Light", dark: "Dark" }[th],
        chk: UI.theme === th, dis: UI.style === "win95", on: () => set("theme", th),
      })),
    ] }];
  }

  // ------------------------------------------------------------ toast
  let toastEl = null, toastT = 0;
  function toast(text) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "toast"; document.body.appendChild(toastEl); }
    toastEl.textContent = text; toastEl.classList.add("on");
    clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove("on"), 1400);
  }
  async function copy(text, what) {
    try { await navigator.clipboard.writeText(text); toast((what || "Text") + " copied"); }
    catch (e) { toast("Copy failed: select and press Ctrl+C"); }
  }

  window.Appearance = { UI, set, ctxMenu, closeMenu, appearanceItems, toast, copy };
})();
