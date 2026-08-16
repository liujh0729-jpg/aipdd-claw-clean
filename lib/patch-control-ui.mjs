#!/usr/bin/env node
// Idempotently inject a boot loading overlay into the OpenClaw Control UI
// (dist/control-ui/index.html), a language picker into the /settings/general
// config page, and an English option into the official overview language
// dropdown. Run on every launch from Mac-Start.command / Windows-Start.bat.
// When the patch is already present (or an upgrade restored the pristine
// template, or the user patched it manually) the file is either skipped or
// re-patched — never duplicated.
import fs from "node:fs";

// CSS block inserted right before </style> in <head>
const CSS = `
      /* openclaw-ui-loading-patch: boot loading overlay */
      #app-loading {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: grid;
        place-items: center;
        align-content: center;
        gap: 16px;
        background: #101418;
        color: #eef4f8;
        /* !important beats OpenClaw's global prefers-reduced-motion rules, which
           flatten every animation/transition to ~0ms and would make the boot
           overlay (spinner + fade-out) appear frozen. */
        transition: opacity 0.4s ease !important;
      }

      #app-loading.app-loading--done {
        opacity: 0;
        pointer-events: none;
      }

      html[data-theme-mode="light"] #app-loading {
        background: #f5f7fa;
        color: #151b21;
      }

      .app-loading__spinner {
        box-sizing: border-box;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        border: 3px solid rgba(148, 163, 184, 0.25);
        border-top-color: #66c2ff;
        /* !important: see #app-loading above (global reduced-motion flattening). */
        animation: app-loading-spin 0.8s linear infinite !important;
      }

      @keyframes app-loading-spin {
        to {
          transform: rotate(360deg);
        }
      }

      .app-loading__text {
        font-size: 0.9rem;
        color: #9fb0bd;
      }

      html[data-theme-mode="light"] .app-loading__text {
        color: #4b5963;
      }
`;

// Overlay element inserted right before <openclaw-app> in <body>
const OVERLAY = `    <!-- openclaw-ui-loading-patch -->
    <div id="app-loading" role="status" aria-live="polite">
      <div class="app-loading__spinner"></div>
      <div class="app-loading__text">Connecting to chat page…</div>
    </div>
    <openclaw-app></openclaw-app>`;

// Language switcher widget inserted right before <openclaw-app> in <body>.
// Options are populated by the LANG_JS block below.
const LANG_WIDGET = `    <!-- openclaw-lang-switcher-patch -->
    <div id="openclaw-lang-switcher">
      <select id="openclaw-lang-select" aria-label="Language / 语言"></select>
    </div>
    <openclaw-app></openclaw-app>`;

// JS helpers inserted right before hideFallback() in the mount-fallback script
const JS_HELPERS = `
        // openclaw-ui-loading-patch
        function chatReady() {
          try {
            var root = app.shadowRoot || app;
            if (!root || root.childElementCount === 0) return false;
            return !!root.querySelector('textarea, [contenteditable="true"], [role="textbox"]');
          } catch (e) {
            return false;
          }
        }

        function createLoading() {
          var div = document.createElement("div");
          div.id = "app-loading";
          div.setAttribute("role", "status");
          div.setAttribute("aria-live", "polite");
          div.innerHTML =
            '<div class="app-loading__spinner"></div>' +
            '<div class="app-loading__text">Connecting to chat page…</div>';
          document.body.insertBefore(div, document.body.firstChild);
          return div;
        }

        function dismissLoading() {
          var loading = document.getElementById("app-loading");
          if (!loading || loading.dataset.dismissed) return;
          loading.dataset.dismissed = "1";
          var minShow = 2000;
          var maxWait = 8000;
          var start = Date.now();
          (function poll() {
            if ((chatReady() && Date.now() - start >= minShow) || Date.now() - start > maxWait) {
              loading.classList.add("app-loading--done");
              window.setTimeout(function () {
                loading.remove();
              }, 500);
              return;
            }
            window.setTimeout(poll, 120);
          })();
        }

        // Re-show the loading overlay when the user opens a session URL in an
        // already-loaded tab (a fragment-only change does not reload the page,
        // so the boot overlay would otherwise never appear again) or when the
        // page is restored from the browser's bfcache.
        function ensureLoadingVisible(force) {
          if (document.getElementById("app-loading")) return;
          if (!force && window.location.hash.indexOf("session=") === -1) return;
          createLoading();
          dismissLoading();
        }
        window.addEventListener("hashchange", function () {
          ensureLoadingVisible(false);
        });
        window.addEventListener("pageshow", function (e) {
          if (e.persisted) ensureLoadingVisible(true);
        });
`;

// Settings-page language picker JS — on /settings/general (config page) inserts
// a Language card right under the page header. Writes the official i18n
// localStorage key (openclaw.i18n.locale) and reloads; defaults to English on
// first visit. The config page is a lit component, so a MutationObserver
// re-inserts the card after each re-render (insert is idempotent).
const SETTINGS_LANG_JS = `
        // openclaw-settings-lang-patch: settings language picker
        (function () {
          var KEY = "openclaw.i18n.locale";
          var LANGS = [
            ["en", "English"],
            ["zh-CN", "简体中文 (Simplified Chinese)"],
            ["zh-TW", "繁體中文 (Traditional Chinese)"],
            ["pt-BR", "Português (Brazilian Portuguese)"],
            ["de", "Deutsch (German)"],
            ["es", "Español (Spanish)"],
            ["ja-JP", "日本語 (Japanese)"],
            ["ko", "한국어 (Korean)"],
            ["fr", "Français (French)"],
            ["hi", "हिन्दी (Hindi)"],
            ["ar", "العربية (Arabic)"],
            ["it", "Italiano (Italian)"],
            ["tr", "Türkçe (Turkish)"],
            ["uk", "Українська (Ukrainian)"],
            ["id", "Bahasa Indonesia (Indonesian)"],
            ["pl", "Polski (Polish)"],
            ["th", "ไทย (Thai)"],
            ["vi", "Tiếng Việt (Vietnamese)"],
            ["nl", "Nederlands (Dutch)"],
            ["fa", "فارسی (Persian)"],
            ["ru", "Русский (Russian)"]
          ];

          // Default to English on first visit (no stored choice yet).
          try {
            if (!localStorage.getItem(KEY)) localStorage.setItem(KEY, "en");
          } catch (e) {}

          function isSettingsGeneral() {
            var p = location.pathname || "";
            return p === "/settings/general" || p === "/config";
          }

          function isLight() {
            var el = document.documentElement;
            return !!el && el.getAttribute("data-theme-mode") === "light";
          }

          function currentLocale() {
            try {
              var stored = localStorage.getItem(KEY);
              if (stored) return stored;
            } catch (e) {}
            return "en";
          }

          function buildCard() {
            var light = isLight();
            var cardBg = light ? "rgba(75, 89, 99, 0.06)" : "rgba(148, 163, 184, 0.06)";
            var cardBorder = light ? "rgba(75, 89, 99, 0.25)" : "rgba(148, 163, 184, 0.25)";
            var text = light ? "#151b21" : "#eef4f8";
            var muted = light ? "#4b5963" : "#9fb0bd";
            var fieldBg = light ? "#f5f7fa" : "#101418";
            var cur = currentLocale();
            var opts = "";
            for (var i = 0; i < LANGS.length; i++) {
              opts +=
                '<option value="' + LANGS[i][0] + '"' +
                (LANGS[i][0] === cur ? " selected" : "") +
                ">" + LANGS[i][1] + "</option>";
            }
            var card = document.createElement("section");
            card.className = "openclaw-lang-settings";
            card.style.cssText =
              "border:1px solid " + cardBorder +
              ";border-radius:12px;padding:16px 18px;margin:16px 24px;" +
              "background:" + cardBg + ";";
            card.innerHTML =
              '<h3 style="margin:0 0 10px;font-size:14px;font-weight:600;color:' + text + '">' +
              "Language / 语言</h3>" +
              '<select style="min-width:280px;padding:7px 10px;border-radius:8px;' +
              "border:1px solid " + cardBorder + ";background:" + fieldBg +
              ";color:" + text + ";font-size:13px;cursor:pointer;outline:none;" + '"' + ">" +
              opts + "</select>" +
              '<p style="margin:8px 0 0;font-size:12px;color:' + muted + '">' +
              "Changes apply after the page reloads. / 修改后刷新页面生效。</p>";
            card.querySelector("select").addEventListener("change", function (e) {
              try {
                localStorage.setItem(KEY, e.target.value);
              } catch (err) {}
              location.reload();
            });
            return card;
          }

          function ensureCard(root) {
            if (!root || root.querySelector(".openclaw-lang-settings")) return;
            var header = root.querySelector("section.content-header");
            if (!header) return;
            header.parentNode.insertBefore(buildCard(), header.nextSibling);
          }

          function watch() {
            if (!isSettingsGeneral()) return;
            var app = document.querySelector("openclaw-app");
            if (!app) return;
            var appRoot = app.shadowRoot || app;
            var page = appRoot.querySelector("openclaw-config-page");
            if (!page) return;
            var pageRoot = page.shadowRoot || page;
            ensureCard(pageRoot);
            if (!pageRoot.__ocLangObserver) {
              pageRoot.__ocLangObserver = new MutationObserver(function () {
                ensureCard(pageRoot);
              });
              pageRoot.__ocLangObserver.observe(pageRoot, {
                childList: true,
                subtree: true
              });
            }
          }

          setInterval(watch, 800);
        })();
`;

// Injects an "English" option into the official overview language dropdown,
// which by design lists translated locales only (English is the built-in
// default and has no entry). Lets users switch back to English from a
// translated UI without touching localStorage.
const OVERVIEW_LANG_JS = `
        // openclaw-overview-lang-patch: add English to the official overview language select
        (function () {
          var KEY = "openclaw.i18n.locale";

          function currentLocale() {
            try {
              var stored = localStorage.getItem(KEY);
              if (stored) return stored;
            } catch (e) {}
            return "en";
          }

          function ensureEnglishOption(sel) {
            var vals = Array.prototype.map.call(sel.options, function (o) {
              return o.value;
            });
            if (vals.indexOf("zh-CN") === -1 || vals.indexOf("en") !== -1) return;
            var opt = document.createElement("option");
            opt.value = "en";
            opt.textContent = "English";
            sel.insertBefore(opt, sel.firstChild);
            if (currentLocale() === "en") sel.value = "en";
          }

          function watch() {
            var p = location.pathname || "";
            if (p !== "/overview" && p !== "/") return;
            var page = document.querySelector("openclaw-overview-page");
            if (!page) return;
            var sel = page.querySelector("select");
            if (!sel) return;
            ensureEnglishOption(sel);
          }

          setInterval(watch, 800);
        })();
`;

function replaceOnce(source, needle, replacement, what) {
  const idx = source.indexOf(needle);
  if (idx === -1) {
    console.error(`[patch-control-ui] anchor not found: ${what}`);
    return null;
  }
  return source.slice(0, idx) + replacement + source.slice(idx + needle.length);
}

// Replace-or-insert the CSS block right before </style>. Running this on every
// launch lets CSS upgrades apply even when the page was already patched by an
// older version of this script (the stale block is swapped, never duplicated).
function upsertCss(html) {
  const styleClose = "</style>";
  const styleIdx = html.indexOf(styleClose);
  if (styleIdx === -1) {
    console.error("[patch-control-ui] anchor not found: </style>");
    return null;
  }
  const marker = "/* openclaw-ui-loading-patch: boot loading overlay */";
  const markerIdx = html.indexOf(marker);
  if (markerIdx !== -1 && markerIdx < styleIdx) {
    return html.slice(0, markerIdx) + CSS + "\n    " + styleClose + html.slice(styleIdx + styleClose.length);
  }
  return html.slice(0, styleIdx) + CSS + "\n    " + styleClose + html.slice(styleIdx + styleClose.length);
}

const target = process.argv[2];
if (!target) {
  console.error("Usage: node patch-control-ui.mjs <path-to-control-ui-index.html>");
  process.exit(1);
}

let html;
try {
  html = fs.readFileSync(target, "utf8");
} catch (err) {
  console.error(`[patch-control-ui] cannot read ${target}: ${err.message}`);
  process.exit(1);
}

const alreadyPatched = html.includes("<!-- openclaw-ui-loading-patch -->");
const settingsLangPatched = html.includes("// openclaw-settings-lang-patch: settings language picker");

// 1) CSS before </style> — always upserted so CSS fixes/upgrades apply
let out = upsertCss(html);
if (out === null) process.exit(1);

if (!alreadyPatched) {
  // 2) Overlay before <openclaw-app>
  const bodyAnchor = "<body>\n    <openclaw-app></openclaw-app>";
  out = replaceOnce(out, bodyAnchor, "<body>\n" + OVERLAY, "body anchor");
  if (out === null) process.exit(1);

  // 3) JS helpers before hideFallback()
  const helperAnchor = "        function hideFallback() {";
  out = replaceOnce(out, helperAnchor, JS_HELPERS + "\n" + helperAnchor, "hideFallback anchor");
  if (out === null) process.exit(1);

  // 4) showFallback() dismisses the overlay before showing the error panel
  const showFallbackAnchor =
    "        function showFallback() {\n          if (appMounted()) return;\n          retryCurrentDocument();";
  out = replaceOnce(
    out,
    showFallbackAnchor,
    "        function showFallback() {\n          if (appMounted()) return;\n          dismissLoading();\n          retryCurrentDocument();",
    "showFallback anchor",
  );
  if (out === null) process.exit(1);

  // 5) whenDefined() callback dismisses the overlay once the SPA is up
  const whenDefinedAnchor =
    "              window.clearTimeout(recoveryTimer);\n              hideFallback();\n            },\n            function () {},";
  out = replaceOnce(
    out,
    whenDefinedAnchor,
    "              window.clearTimeout(recoveryTimer);\n              hideFallback();\n              dismissLoading();\n            },\n            function () {},",
    "whenDefined anchor",
  );
  if (out === null) process.exit(1);
} else {
  console.log("[patch-control-ui] already patched; CSS upgraded.");
}

if (!settingsLangPatched) {
  // 6) Settings language picker JS before hideFallback()
  const langHelperAnchor = "        function hideFallback() {";
  out = replaceOnce(out, langHelperAnchor, SETTINGS_LANG_JS + "\n" + langHelperAnchor, "settings lang JS anchor");
  if (out === null) process.exit(1);
} else {
  console.log("[patch-control-ui] settings language picker already patched.");
}

const overviewLangPatched = html.includes(
  "// openclaw-overview-lang-patch: add English to the official overview language select",
);
if (!overviewLangPatched) {
  // 7) English option for the official overview language dropdown
  const langHelperAnchor = "        function hideFallback() {";
  out = replaceOnce(out, langHelperAnchor, OVERVIEW_LANG_JS + "\n" + langHelperAnchor, "overview lang JS anchor");
  if (out === null) process.exit(1);
} else {
  console.log("[patch-control-ui] overview language picker already patched.");
}

try {
  fs.writeFileSync(target, out, "utf8");
} catch (err) {
  console.error(`[patch-control-ui] cannot write ${target}: ${err.message}`);
  process.exit(1);
}
console.log("[patch-control-ui] patched OK.");
