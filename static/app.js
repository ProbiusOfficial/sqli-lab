/* global fetch, hljs */

const THEME_KEY = "sqliLabTheme";

let levels = [];
let mode = "practice"; // practice | god
let previewTimer = null;

const $ = (id) => document.getElementById(id);

function getThemePreference() {
  return localStorage.getItem(THEME_KEY) || "system";
}

/** 当前界面实际为浅色或深色（用于 hljs 主题） */
function effectiveUiTheme() {
  const p = getThemePreference();
  if (p === "light") return "light";
  if (p === "dark") return "dark";
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyHljsStylesheet() {
  const link = document.getElementById("hljsTheme");
  if (!link) return;
  const eff = effectiveUiTheme();
  const base =
    "https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/";
  const url = base + (eff === "dark" ? "github-dark.min.css" : "github.min.css");
  if (link.getAttribute("href") !== url) {
    link.setAttribute("href", url);
  }
}

function hljsTry(el) {
  if (!el || typeof hljs === "undefined") return;
  const raw = el.textContent;
  if (!raw || !String(raw).trim()) return;
  el.removeAttribute("data-highlighted");
  try {
    hljs.highlightElement(el);
  } catch {
    /* 语言未注册或 CDN 异常时保留纯文本 */
  }
}

function rehighlightVisibleCode() {
  if (mode === "god") {
    const sp = $("sqlPreview");
    if (sp && sp.textContent.trim()) {
      sp.className = "language-sql";
      hljsTry(sp);
    }
    const se = $("sqlExec");
    if (se && se.textContent.trim()) {
      se.className = "language-sql";
      hljsTry(se);
    }
    const sm = $("sqlMeta");
    if (sm && sm.textContent.trim()) {
      sm.className = "language-json";
      hljsTry(sm);
    }
  }
  if (mode === "god" && !$("sourcePanel").classList.contains("hidden")) {
    const sc = $("sourceCode");
    if (sc && sc.textContent.trim()) {
      sc.className = "language-python";
      hljsTry(sc);
    }
  }
}

function applyAppTheme() {
  const pref = getThemePreference();
  document.documentElement.setAttribute("data-theme", pref);
  const sel = $("themeSelect");
  if (sel) sel.value = pref;
  applyHljsStylesheet();
  rehighlightVisibleCode();
}

function resetSourceCode() {
  const el = $("sourceCode");
  if (!el) return;
  el.textContent = "";
  el.className = "language-python";
  el.removeAttribute("data-highlighted");
}

function resetSqlCode(id, langClass) {
  const el = $(id);
  if (!el) return;
  el.textContent = "";
  el.className = langClass;
  el.removeAttribute("data-highlighted");
}

function setMode(next) {
  mode = next === "god" ? "god" : "practice";
  const btn = $("btnMode");
  const godAside = $("godAside");
  const mainGrid = $("mainGrid");
  const term = $("terminalSection");
  const sourcePanel = $("sourcePanel");
  if (mode === "god") {
    btn.textContent = "切换为练习模式";
    godAside.classList.remove("hidden");
    mainGrid.classList.add("layout-god");
    term.classList.remove("hidden");
    sourcePanel.classList.remove("hidden");
    $("ttyFrame").src = "/terminal/";
  } else {
    btn.textContent = "切换为上帝模式";
    godAside.classList.add("hidden");
    mainGrid.classList.remove("layout-god");
    term.classList.add("hidden");
    sourcePanel.classList.add("hidden");
    $("ttyFrame").src = "about:blank";
    resetSqlCode("sqlPreview", "language-sql");
    resetSqlCode("sqlExec", "language-sql");
    resetSqlCode("sqlMeta", "language-json");
    resetSourceCode();
  }
}

function activeLevelId() {
  return $("levelSelect").value;
}

function buildPayload() {
  return {
    level: activeLevelId(),
    mode,
    get: { id: $("get_id").value },
    post: { uname: $("post_uname").value, passwd: $("post_passwd").value },
    cookie: { uname: $("cookie_uname").value },
    headers: {
      "User-Agent": $("hdr_ua").value,
      Referer: $("hdr_ref").value,
    },
  };
}

function previewQueryString() {
  const p = buildPayload();
  const qs = new URLSearchParams();
  qs.set("level", p.level);
  qs.set("mode", p.mode);
  qs.set("id", p.get.id || "");
  qs.set("uname", p.post.uname || "");
  qs.set("passwd", p.post.passwd || "");
  qs.set("cookie_uname", p.cookie.uname || "");
  qs.set("ua", p.headers["User-Agent"] || "");
  qs.set("referer", p.headers.Referer || "");
  return qs.toString();
}

async function refreshPreview() {
  if (mode !== "god") return;
  const qs = previewQueryString();
  const res = await fetch(`/api/sql-preview?${qs}`);
  const data = await res.json();
  const el = $("sqlPreview");
  const text = data.ok ? data.sql_preview || "" : `（预览失败）${data.error || ""}`;
  el.className = "language-sql";
  el.removeAttribute("data-highlighted");
  el.textContent = text;
  hljsTry(el);
}

function schedulePreview() {
  clearTimeout(previewTimer);
  previewTimer = setTimeout(() => {
    refreshPreview().catch(() => {});
  }, 220);
}

async function loadLevels() {
  const res = await fetch("/api/levels");
  const data = await res.json();
  levels = data.levels || [];
  const sel = $("levelSelect");
  sel.innerHTML = "";
  for (const lv of levels) {
    const opt = document.createElement("option");
    opt.value = lv.id;
    opt.textContent = `${lv.id} · ${lv.title}`;
    sel.appendChild(opt);
  }
  updateMeta();
}

function updateMeta() {
  const id = activeLevelId();
  const idx = levels.findIndex((x) => x.id === id);
  $("levelMeta").textContent =
    idx >= 0 ? `进度：${idx + 1} / ${levels.length}` : "";
}

async function loadGodSource() {
  if (mode !== "god") return;
  const id = activeLevelId();
  const res = await fetch(`/api/god/source?level=${encodeURIComponent(id)}`);
  const data = await res.json();
  const el = $("sourceCode");
  el.className = "language-python";
  el.removeAttribute("data-highlighted");
  el.textContent = data.ok ? data.source : data.error || "读取失败";
  hljsTry(el);
}

async function submit() {
  const body = buildPayload();
  const res = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  $("echo").innerHTML = data.echo_html || "";

  if (mode === "god") {
    const execEl = $("sqlExec");
    execEl.className = "language-sql";
    execEl.removeAttribute("data-highlighted");
    execEl.textContent = data.executed_sql || "";
    hljsTry(execEl);

    const metaEl = $("sqlMeta");
    let metaText = "";
    if (data.mysql) {
      metaText = JSON.stringify(
        {
          mysql: data.mysql,
          elapsed_ms: data.elapsed_ms,
          rowcount: data.rowcount,
        },
        null,
        2
      );
    } else {
      metaText = JSON.stringify(
        { ok: true, elapsed_ms: data.elapsed_ms, rowcount: data.rowcount },
        null,
        2
      );
    }
    metaEl.className = "language-json";
    metaEl.removeAttribute("data-highlighted");
    metaEl.textContent = metaText;
    hljsTry(metaEl);
  }
  if (mode === "god") {
    await loadGodSource().catch(() => {});
  }
}

function wireTabs() {
  document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-tab");
      document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      $(`panel-${tab}`).classList.add("active");
    });
  });
}

async function resetDb() {
  const token = $("resetToken").value || "";
  const res = await fetch("/api/admin/reset", {
    method: "POST",
    headers: { "X-Reset-Token": token },
  });
  const data = await res.json();
  alert(data.ok ? data.message : data.error || "重置失败");
}

function wireInputsPreview() {
  const ids = [
    "get_id",
    "post_uname",
    "post_passwd",
    "cookie_uname",
    "hdr_ua",
    "hdr_ref",
  ];
  for (const id of ids) {
    $(id).addEventListener("input", () => {
      if (mode === "god") schedulePreview();
    });
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  wireTabs();
  wireInputsPreview();

  const themeSel = $("themeSelect");
  themeSel.value = getThemePreference();
  document.documentElement.setAttribute("data-theme", getThemePreference());
  applyHljsStylesheet();

  themeSel.addEventListener("change", () => {
    localStorage.setItem(THEME_KEY, themeSel.value);
    applyAppTheme();
  });

  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      if (getThemePreference() === "system") {
        applyHljsStylesheet();
        rehighlightVisibleCode();
      }
    });

  $("btnMode").addEventListener("click", () => {
    setMode(mode === "god" ? "practice" : "god");
    if (mode === "god") {
      refreshPreview().catch(() => {});
      loadGodSource().catch(() => {});
    }
  });

  $("btnSubmit").addEventListener("click", () => submit().catch((e) => alert(String(e))));

  $("levelSelect").addEventListener("change", () => {
    updateMeta();
    if (mode === "god") {
      schedulePreview();
      loadGodSource().catch(() => {});
    }
  });

  $("btnPrev").addEventListener("click", () => {
    const sel = $("levelSelect");
    sel.selectedIndex = Math.max(0, sel.selectedIndex - 1);
    sel.dispatchEvent(new Event("change"));
  });
  $("btnNext").addEventListener("click", () => {
    const sel = $("levelSelect");
    sel.selectedIndex = Math.min(sel.options.length - 1, sel.selectedIndex + 1);
    sel.dispatchEvent(new Event("change"));
  });

  $("btnReset").addEventListener("click", () => resetDb().catch((e) => alert(String(e))));

  await loadLevels();
});
