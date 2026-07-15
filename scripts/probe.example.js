// Example probe for scripts/browser_probe.mjs — inspect theme / notification /
// markdown rendering of a pysepal app. Pass it with `--eval @scripts/probe.example.js`.
//
// A probe is a single JS expression (here an IIFE) evaluated in the live page.
// It must return a JSON-serializable value. Read the DOM and computed styles —
// that is the source of truth for "what the user actually sees".
(() => {
  const themeClass = (el) =>
    el ? (el.className.match(/theme--\w+/) || ["(none)"])[0] : null;
  const apps = [...document.querySelectorAll(".v-application")];
  const md = document.querySelector(".solara-markdown");
  const pill = document.querySelector(".pill-wrapper");
  const notifRoot = pill && pill.closest(".theme-dark, .theme-light");

  return {
    url: location.href,
    // Vuetify stamps theme--dark / theme--light on its app roots — the reliable
    // cross-runtime signal for "is the app dark?".
    v_application_themes: apps.map(themeClass),
    any_v_application_dark: !!document.querySelector(
      ".v-application.theme--dark"
    ),
    // Notification pill/logger: one instance expected; theme + resolved bg.
    pill_count: document.querySelectorAll(".pill-wrapper").length,
    toast_stack_count: document.querySelectorAll(".toast-stack").length,
    notif_root_theme: notifRoot
      ? (notifRoot.className.match(/theme-\w+/) || ["(none)"])[0]
      : "none",
    pill_bg: (() => {
      const b = document.querySelector(
        ".pill-log-btn, .pill-container, .pill-log"
      );
      return b ? getComputedStyle(b).backgroundColor : null;
    })(),
    // solara.Markdown carries JupyterLab's jp-RenderedHTMLCommon class; check its
    // computed color follows the theme (white in dark).
    markdown_color: md ? getComputedStyle(md).color : null,
    // JupyterLab puts a single-dash `theme-light`/`theme-dark` on <body>; worth
    // knowing it's there, since it collides with pysepal's notification classes.
    body_theme_single_dash:
      [...document.body.classList].filter(
        (c) => c === "theme-light" || c === "theme-dark"
      )[0] || null,
  };
})();
