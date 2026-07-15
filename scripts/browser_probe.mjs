#!/usr/bin/env node
/**
 * browser_probe.mjs — drive a headless Chrome against a URL over the Chrome
 * DevTools Protocol (CDP) and evaluate JavaScript in the live page, printing
 * the (JSON-serialized) result to stdout.
 *
 * Purpose
 * -------
 * A dependency-free way to *test pysepal apps the way a browser sees them* —
 * inspect the rendered DOM, read computed styles, assert theme/layout state,
 * or compare the same app across runtimes (e.g. `solara run` vs Voila). It was
 * written to debug Solara/Voila styling parity, but it is a general tool: any
 * question of the form "what does this actually render to?" can be answered by
 * passing a probe expression.
 *
 * Requirements
 * ------------
 *   - Node >= 22 (uses the built-in global `WebSocket`; no npm install).
 *   - A Chrome/Chromium binary on PATH (or pass --chrome <path>).
 *
 * Usage
 * -----
 *   node scripts/browser_probe.mjs --url http://127.0.0.1:8900/ \
 *        --wait '.pill-wrapper' --settle 2500 --eval @scripts/probe.example.js
 *
 *   node scripts/browser_probe.mjs --url http://127.0.0.1:8910/ \
 *        --eval "({ title: document.title })"
 *
 * Options
 * -------
 *   --url <url>          (required) page to load
 *   --eval <expr|@file>  JS expression to evaluate, or @path to a .js file
 *                        holding one expression (an IIFE is the usual shape).
 *                        Must return a JSON-serializable value. Default: title
 *                        + body text length.
 *   --wait <selector>    poll until this selector exists (else --timeout)
 *   --settle <ms>        extra wait after ready, for layout/theme (default 2000)
 *   --timeout <ms>       readiness budget (default 30000)
 *   --force-theme <t>    set localStorage ':solara:theme.variant' to "dark" or
 *                        "light" and reload (Solara only — Voila ignores it)
 *   --chrome <path>      Chrome binary (default: autodetect)
 *   --keep-open          leave Chrome running (debugging the probe itself)
 *
 * Notes / gotchas (learned the hard way)
 * --------------------------------------
 *   - Each run creates a FRESH browser session and, for server apps, a fresh
 *     kernel — it does NOT reuse your logged-in tab. That's usually what you
 *     want for reproducibility, but auth-gated pages may render empty.
 *   - Never clean up Chrome with `pkill -f <pattern>` where <pattern> also
 *     appears in the launching script's own argv — it matches (and kills) your
 *     own shell. This tool tracks the spawned PID and kills only that.
 *   - Inside a restricted sandbox Chrome may be signal-killed on launch; run it
 *     from a normal shell, or disable the sandbox for the launching command.
 *   - ipyvue injects Vue `<style scoped>` as GLOBAL css (no data-v attribute),
 *     so computed styles can be affected by ancestor classes you don't expect
 *     (e.g. JupyterLab sets `theme-light` on <body>). Probing computed styles
 *     is how you catch that.
 */
import { spawn, execSync } from "node:child_process";
import { setTimeout as sleep } from "node:timers/promises";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

function argVal(name, def) {
  const i = process.argv.indexOf(name);
  return i >= 0 && i + 1 < process.argv.length ? process.argv[i + 1] : def;
}

const URL = argVal("--url");
if (!URL) {
  console.error("--url is required. See the header of this file for usage.");
  process.exit(2);
}
const WAIT = argVal("--wait");
const SETTLE = parseInt(argVal("--settle", "2000"), 10);
const TIMEOUT = parseInt(argVal("--timeout", "30000"), 10);
const FORCE_THEME = argVal("--force-theme");
const KEEP_OPEN = process.argv.includes("--keep-open");
let EVAL = argVal("--eval");
if (EVAL && EVAL.startsWith("@")) EVAL = readFileSync(EVAL.slice(1), "utf8");
if (!EVAL)
  EVAL =
    "({ title: document.title, bodyTextLen: document.body.innerText.length })";

function findChrome() {
  const explicit = argVal("--chrome");
  if (explicit) return explicit;
  for (const c of [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
  ]) {
    try {
      return execSync(`command -v ${c}`, {
        stdio: ["ignore", "pipe", "ignore"],
      })
        .toString()
        .trim();
    } catch {
      /* try next */
    }
  }
  throw new Error("No chrome/chromium found on PATH; pass --chrome <path>");
}

// ---- minimal CDP client over the built-in WebSocket ----
let msgId = 0;
const pending = new Map();

function send(ws, method, params = {}, sessionId) {
  const id = ++msgId;
  const payload = { id, method, params };
  if (sessionId) payload.sessionId = sessionId;
  ws.send(JSON.stringify(payload));
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => {
      pending.delete(id);
      reject(new Error("CDP timeout: " + method));
    }, 20000);
    pending.set(id, {
      resolve: (v) => {
        clearTimeout(t);
        resolve(v);
      },
      reject: (e) => {
        clearTimeout(t);
        reject(e);
      },
    });
  });
}

async function evaluate(ws, sessionId, expr) {
  // Evaluate `expr` as-is. Runtime.evaluate returns the completion value, so
  // both a parenthesized expression `({...})` and an IIFE statement
  // `(() => {...})();` work. (Wrapping in extra parens would break the latter.)
  const r = await send(
    ws,
    "Runtime.evaluate",
    { expression: expr, returnByValue: true, awaitPromise: true },
    sessionId
  );
  if (r.exceptionDetails)
    throw new Error("eval error: " + JSON.stringify(r.exceptionDetails));
  return r.result.value;
}

async function main() {
  const chromeBin = findChrome();
  const udd = mkdtempSync(join(tmpdir(), "browser-probe-"));
  const chrome = spawn(
    chromeBin,
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--no-first-run",
      "--no-default-browser-check",
      `--user-data-dir=${udd}`,
      "--remote-debugging-port=0", // ephemeral; real port is printed to stderr
      "--remote-allow-origins=*",
      "about:blank",
    ],
    { stdio: ["ignore", "ignore", "pipe"] }
  );

  const cleanup = () => {
    if (KEEP_OPEN) return;
    try {
      chrome.kill("SIGKILL");
    } catch {}
    try {
      rmSync(udd, { recursive: true, force: true });
    } catch {}
  };
  process.on("exit", cleanup);
  process.on("SIGINT", () => {
    cleanup();
    process.exit(130);
  });

  // Chrome prints "DevTools listening on ws://127.0.0.1:<port>/devtools/browser/..."
  const wsUrl = await new Promise((resolve, reject) => {
    let buf = "";
    const to = setTimeout(
      () => reject(new Error("Chrome never reported a DevTools endpoint")),
      15000
    );
    chrome.stderr.on("data", (d) => {
      buf += d.toString();
      const m = buf.match(/ws:\/\/\S+/);
      if (m) {
        clearTimeout(to);
        resolve(m[0]);
      }
    });
    chrome.on("exit", (code) => {
      clearTimeout(to);
      reject(new Error("Chrome exited early (code " + code + ")"));
    });
  });

  const ws = await new Promise((resolve, reject) => {
    const s = new WebSocket(wsUrl);
    s.addEventListener("open", () => resolve(s), { once: true });
    s.addEventListener(
      "error",
      () => reject(new Error("WebSocket connect failed")),
      { once: true }
    );
  });
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const p = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) p.reject(new Error(JSON.stringify(msg.error)));
      else p.resolve(msg.result);
    }
  });

  const { targetId } = await send(ws, "Target.createTarget", { url: URL });
  const { sessionId } = await send(ws, "Target.attachToTarget", {
    targetId,
    flatten: true,
  });
  await send(ws, "Page.enable", {}, sessionId);
  await send(ws, "Runtime.enable", {}, sessionId);

  const waitReady = async () => {
    const start = Date.now();
    while (Date.now() - start < TIMEOUT) {
      try {
        const ready = WAIT
          ? await evaluate(
              ws,
              sessionId,
              `!!document.querySelector(${JSON.stringify(WAIT)})`
            )
          : await evaluate(ws, sessionId, `document.readyState === 'complete'`);
        if (ready) return;
      } catch {
        /* keep polling */
      }
      await sleep(500);
    }
  };

  await waitReady();
  await sleep(SETTLE);

  if (FORCE_THEME === "dark" || FORCE_THEME === "light") {
    await evaluate(
      ws,
      sessionId,
      `localStorage.setItem(':solara:theme.variant', '"${FORCE_THEME}"'), true`
    );
    await send(ws, "Page.reload", {}, sessionId);
    await waitReady();
    await sleep(SETTLE);
  }

  const value = await evaluate(ws, sessionId, EVAL);
  console.log(JSON.stringify(value, null, 2));

  try {
    await send(ws, "Target.closeTarget", { targetId });
  } catch {}
  ws.close();
  cleanup();
}

main().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
