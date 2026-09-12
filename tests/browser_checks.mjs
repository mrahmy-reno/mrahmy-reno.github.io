/**
 * Browser-level checks (puppeteer-core + axe-core) against the built site.
 *
 * Runs over the publish root (`docs/`) served from a throwaway local static server, so the
 * result is independent of how the site is deployed. Produces:
 *   - rendered-text/<page>.txt   (rendered visible text, for the A1/D1 provenance + A12 scans)
 *   - axe/<page>.json            (axe-core results per page)
 *   - console/<page>.json        (console + pageerror + network log per page)
 *   - overflow.json              (A6: per-width overflow assertions)
 *   - first-screen.json          (A2/D2: zero-scroll first-viewport assertions)
 *   - keyboard.json              (A4: tab walk + focus indicator)
 *   - reduced-motion.json        (A4/D4)
 *   - progressive-enhancement.json (JS disabled still usable)
 *   - print.json + print/*.pdf   (A17)
 *   - screenshots/*.png          (A6/D6: 8 screenshots)
 *
 * Usage: node tests/browser_checks.mjs --docs docs --out <evidence dir> [--port 8099]
 * Exit 0 = all browser checks passed.
 */

import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..");

const args = new Map();
for (let i = 2; i < process.argv.length; i += 2) {
  args.set(process.argv[i].replace(/^--/, ""), process.argv[i + 1]);
}
const DOCS = path.resolve(REPO, args.get("docs") || "docs");
const OUT = path.resolve(args.get("out") || path.join(REPO, "evidence", "B1-03"));
const PORT = Number(args.get("port") || 8099);
const CHROME = process.env.CHROME_PATH || "/usr/bin/google-chrome";

const SLUGS = ["sama-soc-triage", "smartops-soc-app", "milo-ai-employee", "pulsesec",
  "tonsy-gpt", "smart-care", "halalbot", "forwheelz", "email-mcp", "voice-agent-core"];
const PAGES = ["index.html", ...SLUGS.map((s) => `projects/${s}.html`), "404.html"];
const WIDTHS = [360, 768, 1024, 1440];

const failures = [];
const results = {};
let checkCount = 0;

function check(cond, label, detail = "") {
  checkCount += 1;
  const line = `[${cond ? "PASS" : "FAIL"}] ${label}${detail ? " :: " + detail : ""}`;
  console.log(line);
  if (!cond) failures.push(label);
  return cond;
}

function mkdirp(p) { fs.mkdirSync(p, { recursive: true }); }

const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
  ".xml": "application/xml", ".txt": "text/plain; charset=utf-8",
};

function startServer() {
  const server = http.createServer((req, res) => {
    const urlPath = decodeURIComponent(req.url.split("?")[0]);
    let file = path.join(DOCS, urlPath);
    if (urlPath.endsWith("/")) file = path.join(file, "index.html");
    if (!file.startsWith(DOCS)) { res.writeHead(403); res.end("no"); return; }
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      const nf = path.join(DOCS, "404.html");
      if (fs.existsSync(nf)) { res.writeHead(404, { "content-type": "text/html" }); res.end(fs.readFileSync(nf)); }
      else { res.writeHead(404); res.end("not found"); }
      return;
    }
    res.writeHead(200, { "content-type": MIME[path.extname(file)] || "application/octet-stream" });
    res.end(fs.readFileSync(file));
  });
  return new Promise((resolve) => server.listen(PORT, "127.0.0.1", () => resolve(server)));
}

const AXE_SOURCE = fs.readFileSync(
  path.join(REPO, "node_modules", "axe-core", "axe.min.js"), "utf8");

/** Extract rendered text: everything the user can read (skips script/style/noscript/template),
 *  and also records each element's client rect so we can tell what is inside the viewport. */
function extractRenderedText() {
  const skip = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE", "svg", "SVG"]);
  const parts = [];
  (function walk(node) {
    if (node.nodeType === 3) {
      const t = node.nodeValue.replace(/\s+/g, " ");
      if (t.trim()) parts.push(t.trim());
      return;
    }
    if (node.nodeType !== 1) return;
    if (skip.has(node.tagName)) return;
    const cs = window.getComputedStyle(node);
    const hidden = node.hasAttribute("hidden") || cs.display === "none";
    for (const child of node.childNodes) {
      if (hidden) {
        // print-only content is display:none on screen; still record it (stricter scan)
        walk(child);
      } else {
        walk(child);
      }
    }
  })(document.body);
  return parts.join("\n");
}

/** Resolve the visible-text items of the first viewport at zero scroll.
 *  Only rendered (not display:none / visibility:hidden / zero-area) elements count. */
function firstScreenProbe(strings) {
  const out = { viewport: { w: window.innerWidth, h: window.innerHeight }, strings: {} };
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const found = new Map(strings.map((s) => [s, []]));
  let node;
  while ((node = walker.nextNode())) {
    const parent = node.parentElement;
    if (!parent) continue;
    const tag = parent.tagName;
    if (tag === "SCRIPT" || tag === "STYLE" || tag === "NOSCRIPT") continue;
    const cs = window.getComputedStyle(parent);
    if (cs.display === "none" || cs.visibility === "hidden" || parent.hasAttribute("hidden")) {
      continue;
    }
    const r = parent.getBoundingClientRect();
    if (r.width <= 0 && r.height <= 0) continue;
    const text = node.nodeValue;
    for (const s of strings) {
      if (text.includes(s)) {
        found.get(s).push({ top: Math.round(r.top), bottom: Math.round(r.bottom),
          left: Math.round(r.left), right: Math.round(r.right) });
      }
    }
  }
  for (const [s, rects] of found) {
    out.strings[s] = {
      present: rects.length > 0,
      inViewport: rects.some((r) => r.top < window.innerHeight && r.bottom > 0 &&
        r.left < window.innerWidth && r.right > 0),
      rects,
    };
  }
  return out;
}

function overflowProbe() {
  const de = document.documentElement;
  const vw = window.innerWidth;
  const offenders = [];
  document.querySelectorAll("body *").forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && (r.right > vw + 1 || r.left < -1)) {
      const cs = window.getComputedStyle(el);
      if (cs.position === "fixed" || cs.visibility === "hidden") return;
      offenders.push({ tag: el.tagName, cls: el.className.toString().slice(0, 60),
        left: Math.round(r.left), right: Math.round(r.right), vw });
    }
  });
  return {
    vw,
    scrollWidth: de.scrollWidth, clientWidth: de.clientWidth,
    bodyScrollWidth: document.body.scrollWidth,
    horizontalOverflow: de.scrollWidth > de.clientWidth,
    offenders: offenders.slice(0, 8),
  };
}

async function main() {
  mkdirp(OUT);
  for (const d of ["rendered-text", "axe", "console", "screenshots", "print"]) {
    mkdirp(path.join(OUT, d));
  }

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
      "--font-render-hinting=none"],
  });
  const server = await startServer();
  const origin = `http://127.0.0.1:${PORT}`;
  console.log(`server: ${origin} -> ${DOCS}`);
  console.log(`chrome: ${await browser.version()}`);

  // ---------------------------------------------------------------- per page
  const axeSummary = {};
  const consoleSummary = {};
  const thirdParty = new Set();

  for (const rel of PAGES) {
    const url = `${origin}/${rel}`;
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900, deviceScaleFactor: 1 });
    const messages = [];
    const errors = [];
    const warnings = [];
    page.on("console", (m) => {
      const entry = { type: m.type(), text: m.text() };
      messages.push(entry);
      if (m.type() === "error") errors.push(entry);
      if (m.type() === "warning") warnings.push(entry);
    });
    page.on("pageerror", (e) => errors.push({ type: "pageerror", text: String(e) }));
    page.on("requestfailed", (r) => errors.push({ type: "requestfailed", url: r.url(),
      text: r.failure() ? r.failure().errorText : "" }));
    page.on("response", (r) => {
      const u = new URL(r.url());
      if (!u.hostname.startsWith("127.0.0.1") && u.hostname !== "localhost") {
        thirdParty.add(`${rel} -> ${r.url()}`);
      }
    });
    await page.goto(url, { waitUntil: "load" });
    await new Promise((r) => setTimeout(r, 120));

    const text = await page.evaluate(extractRenderedText);
    fs.writeFileSync(path.join(OUT, "rendered-text",
      rel.replace(/\//g, "_").replace(/\.html$/, "") + ".txt"), text);

    // B1-05 / D-03 guard. `styles.css` sets `.section{content-visibility:auto}`, which keeps
    // off-screen sections unpainted. A renderer that reads only the painted/laid-out surface can
    // therefore silently drop whole sections and still look "complete" (that is exactly how a
    // truncated dump passed for a full one during B1-04). Never trust a text dump without proving
    // it reaches the LAST section: this walks the last section's own text nodes and asserts a
    // marker from it is present in the extracted dump.
    const coverage = await page.evaluate(() => {
      const sections = [...document.querySelectorAll("section")];
      const last = sections[sections.length - 1];
      let marker = "";
      if (last) {
        const walker = document.createTreeWalker(last, NodeFilter.SHOW_TEXT);
        let n;
        while ((n = walker.nextNode())) {
          const t = n.nodeValue.replace(/\s+/g, " ").trim();
          if (t) marker = t;
        }
      }
      return { sections: sections.length, lastMarker: marker };
    });
    if (!results.coverage) results.coverage = {};
    results.coverage[rel] = { ...coverage, dumpChars: text.length };
    check(coverage.sections >= 1 && coverage.lastMarker.length > 0 &&
      text.includes(coverage.lastMarker),
      `rendered-text dump reaches the last section on ${rel} (no silent content-visibility truncation)`,
      JSON.stringify({ sections: coverage.sections, lastMarker: coverage.lastMarker,
        dumpChars: text.length }));

    // axe
    await page.evaluate(AXE_SOURCE);
    const axe = await page.evaluate(async () => {
      const r = await window.axe.run(document, {
        resultTypes: ["violations"],
        rules: { "color-contrast": { enabled: true } },
      });
      return {
        violations: r.violations.map((v) => ({ id: v.id, impact: v.impact,
          help: v.help, nodes: v.nodes.length,
          targets: v.nodes.slice(0, 5).map((n) => n.target.join(" ")) })),
        passes: r.passes.length,
        incomplete: r.incomplete.map((v) => ({ id: v.id, impact: v.impact,
          nodes: v.nodes.length })),
      };
    });
    axeSummary[rel] = axe;
    fs.writeFileSync(path.join(OUT, "axe", rel.replace(/\//g, "_") + ".json"),
      JSON.stringify(axe, null, 2));

    const serious = axe.violations.filter((v) => v.impact === "critical" || v.impact === "serious");
    check(serious.length === 0, `axe: 0 critical/0 serious on ${rel}`,
      serious.length ? JSON.stringify(serious) : `${axe.passes} rules passed`);

    // structure: exactly one h1, no skipped heading level on the way down
    const structure = await page.evaluate(() => {
      const hs = [...document.querySelectorAll("h1,h2,h3,h4,h5,h6")];
      const levels = hs.map((h) => Number(h.tagName[1]));
      const skips = [];
      for (let i = 1; i < levels.length; i += 1) {
        if (levels[i] - levels[i - 1] > 1) {
          skips.push(`${hs[i - 1].tagName} -> ${hs[i].tagName} (${hs[i].textContent.trim().slice(0, 30)})`);
        }
      }
      return {
        h1: hs.filter((h) => h.tagName === "H1").map((h) => h.textContent.trim()),
        skips,
        counts: hs.reduce((acc, h) => { acc[h.tagName] = (acc[h.tagName] || 0) + 1; return acc; }, {}),
      };
    });
    check(structure.h1.length === 1, `exactly one h1 on ${rel}`, JSON.stringify(structure.h1));
    check(structure.skips.length === 0, `heading order is logical on ${rel}`,
      structure.skips.length ? JSON.stringify(structure.skips) : JSON.stringify(structure.counts));
    check(errors.length === 0, `console: 0 errors on ${rel}`,
      errors.length ? JSON.stringify(errors.slice(0, 3)) : "clean");
    check(warnings.length === 0, `console: 0 warnings on ${rel}`,
      warnings.length ? JSON.stringify(warnings.slice(0, 3)) : "clean");
    consoleSummary[rel] = { messages, errors, warnings };
    fs.writeFileSync(path.join(OUT, "console", rel.replace(/\//g, "_") + ".json"),
      JSON.stringify({ messages, errors, warnings }, null, 2));
    await page.close();
  }

  check(thirdParty.size === 0, "network: 0 third-party requests on any page",
    thirdParty.size ? JSON.stringify([...thirdParty]) : "0 requests to non-localhost origins");
  fs.writeFileSync(path.join(OUT, "network.json"),
    JSON.stringify({ thirdParty: [...thirdParty] }, null, 2));

  // ---------------------------------------------------------------- first screen (A2/D2)
  const firstScreen = {};
  for (const [w, h] of [[1366, 768], [390, 844]]) {
    const page = await browser.newPage();
    await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 });
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    const probe = await page.evaluate(firstScreenProbe, [
      "Mohammed Tawfiq Rahmy", "Solutions Engineer | Mechatronics × AI Systems",
      "AI Solutions Engineer", "Renosystems",
    ]);
    const link = await page.evaluate(() => {
      const a = [...document.querySelectorAll('a[href^="https://www.linkedin.com"]')]
        .map((el) => {
          const r = el.getBoundingClientRect();
          const cs = getComputedStyle(el);
          return { href: el.href, text: el.textContent.trim(),
            top: Math.round(r.top), bottom: Math.round(r.bottom),
            visible: r.top < window.innerHeight && r.bottom > 0 && cs.display !== "none" &&
              cs.visibility !== "hidden" };
        });
      return a;
    });
    firstScreen[`${w}x${h}`] = { probe, linkedinLinks: link, scrollY: await page.evaluate(() => window.scrollY) };
    for (const s of Object.keys(probe.strings)) {
      check(probe.strings[s].inViewport, `first screen ${w}x${h} (no scroll): ${s}`,
        JSON.stringify(probe.strings[s].rects[0] || null));
    }
    check(link.some((l) => l.visible), `first screen ${w}x${h}: LinkedIn link visible`,
      JSON.stringify(link.slice(0, 2)));
    await page.close();
  }
  fs.writeFileSync(path.join(OUT, "first-screen.json"), JSON.stringify(firstScreen, null, 2));

  // ---------------------------------------------------------------- overflow + screenshots
  const overflow = {};
  for (const rel of ["index.html", "projects/sama-soc-triage.html"]) {
    overflow[rel] = {};
    for (const w of WIDTHS) {
      const page = await browser.newPage();
      await page.setViewport({ width: w, height: 900, deviceScaleFactor: 1 });
      await page.goto(`${origin}/${rel}`, { waitUntil: "load" });
      // scroll the whole page first: off-screen sections use content-visibility: auto, so this
      // forces every section to be rendered before the overflow probe and the screenshot (the
      // screenshots must not contain unpainted regions).
      await page.evaluate(async () => {
        const h = document.body.scrollHeight;
        for (let y = 0; y < h; y += 400) {
          window.scrollTo(0, y);
          await new Promise((r) => setTimeout(r, 25));
        }
        window.scrollTo(0, 0);
        await new Promise((r) => setTimeout(r, 60));
      });
      const res = await page.evaluate(overflowProbe);
      overflow[rel][w] = res;
      check(!res.horizontalOverflow, `no horizontal overflow: ${rel} @ ${w}px`,
        `scrollWidth=${res.scrollWidth} clientWidth=${res.clientWidth} offenders=${res.offenders.length}`);
      const name = `${rel.replace(/\//g, "_").replace(/\.html$/, "")}-${w}.png`;
      // content-visibility: auto keeps off-screen sections unpainted in a beyond-viewport
      // capture; override it for the screenshot so the artefact shows the real layout.
      await page.addStyleTag({ content: ".section{content-visibility:visible !important}" });
      await page.evaluate(async () => {
        const h = document.body.scrollHeight;
        for (let y = 0; y < h; y += 400) {
          window.scrollTo(0, y);
          await new Promise((r) => setTimeout(r, 15));
        }
        window.scrollTo(0, 0);
        await new Promise((r) => setTimeout(r, 80));
      });
      await page.screenshot({ path: path.join(OUT, "screenshots", name), fullPage: true });
      await page.close();
    }
  }
  fs.writeFileSync(path.join(OUT, "overflow.json"), JSON.stringify(overflow, null, 2));
  const shotCount = fs.readdirSync(path.join(OUT, "screenshots")).filter((f) => f.endsWith(".png")).length;
  check(shotCount === 8, "8 responsive screenshots captured", `found ${shotCount}`);

  // ---------------------------------------------------------------- keyboard walk (A4)
  {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    const stops = [];
    for (let i = 0; i < 22; i += 1) {
      await page.keyboard.press("Tab");
      const info = await page.evaluate(() => {
        const el = document.activeElement;
        if (!el) return null;
        const cs = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return {
          tag: el.tagName, text: (el.textContent || "").trim().slice(0, 40),
          href: el.getAttribute ? el.getAttribute("href") : null,
          id: el.id || null,
          outlineStyle: cs.outlineStyle, outlineWidth: cs.outlineWidth,
          focusVisible: cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) > 0,
          inViewport: r.top < window.innerHeight && r.bottom > 0,
        };
      });
      stops.push(info);
    }
    const first = stops[0];
    check(!!first && first.tag === "A" && /skip to content/i.test(first.text),
      "skip-to-content is the first focusable element", JSON.stringify(first));
    const unique = new Set(stops.filter(Boolean).map((s) => `${s.tag}:${s.text}:${s.href}`));
    check(unique.size >= 20, "tab walk advances without a keyboard trap",
      `${unique.size} distinct stops of ${stops.length} tabs`);
    const noIndicator = stops.filter((s) => s && !s.focusVisible);
    check(noIndicator.length === 0, "every tab stop has a visible focus indicator",
      noIndicator.length ? JSON.stringify(noIndicator.slice(0, 3)) : "all stops outlined");
    // skip link actually moves focus into main
    await page.evaluate(() => { document.querySelector(".skip-link").focus(); });
    await page.keyboard.press("Enter");
    const afterSkip = await page.evaluate(() => {
      const m = document.querySelector("main");
      return { hash: location.hash, mainTop: Math.round(m.getBoundingClientRect().top),
        active: document.activeElement.tagName };
    });
    check(afterSkip.hash === "#main" || Math.abs(afterSkip.mainTop) < 200,
      "skip link moves to main content", JSON.stringify(afterSkip));
    fs.writeFileSync(path.join(OUT, "keyboard.json"), JSON.stringify({ stops, afterSkip }, null, 2));
    await page.close();
  }

  // ---------------------------------------------------------------- reduced motion (A4/D4)
  {
    const page = await browser.newPage();
    await page.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    const motion = await page.evaluate(() => {
      const secs = (v) => {
        const parts = String(v).split(",").map((x) => x.trim());
        return Math.max(...parts.map((p) => {
          const n = parseFloat(p);
          if (Number.isNaN(n)) return 0;
          return p.endsWith("ms") ? n / 1000 : n;
        }));
      };
      const out = [];
      document.querySelectorAll("body *").forEach((el) => {
        const cs = getComputedStyle(el);
        const t = secs(cs.transitionDuration);
        const a = secs(cs.animationDuration);
        if ((t > 0.01 && cs.transitionProperty !== "none") ||
            (a > 0.01 && cs.animationName !== "none")) {
          out.push({ tag: el.tagName, cls: el.className.toString().slice(0, 40),
            transitionDuration: cs.transitionDuration, animationDuration: cs.animationDuration });
        }
      });
      return { offenders: out.slice(0, 5), total: out.length,
        htmlScrollBehavior: getComputedStyle(document.documentElement).scrollBehavior };
    });
    check(motion.total === 0, "prefers-reduced-motion: no non-essential animation/transition runs",
      JSON.stringify(motion));
    fs.writeFileSync(path.join(OUT, "reduced-motion.json"), JSON.stringify(motion, null, 2));
    await page.close();
  }

  // ---------------------------------------------------------------- layout shift (CLS)
  {
    const page = await browser.newPage();
    await page.evaluateOnNewDocument(() => {
      window.__cls = 0;
      window.__shifts = [];
      try {
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              window.__cls += entry.value;
              window.__shifts.push({ value: entry.value, sources: (entry.sources || [])
                .map((s) => (s.node ? s.node.nodeName + "." + (s.node.className || "") : "?")) });
            }
          }
        }).observe({ type: "layout-shift", buffered: true });
      } catch (e) { window.__clsProbeError = String(e); }
    });
    await page.setViewport({ width: 412, height: 823, deviceScaleFactor: 1 });
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    await new Promise((r) => setTimeout(r, 1500));
    const cls = await page.evaluate(() => ({ cls: window.__cls, shifts: window.__shifts,
      error: window.__clsProbeError || null }));
    check(cls.error === null, "layout-shift observer installed", JSON.stringify(cls.error));
    check(cls.cls < 0.1, "cumulative layout shift on mobile viewport < 0.1",
      `CLS=${cls.cls.toFixed(4)} shifts=${JSON.stringify(cls.shifts)}`);
    fs.writeFileSync(path.join(OUT, "layout-shift.json"), JSON.stringify(cls, null, 2));
    await page.close();
  }

  // ---------------------------------------------------------------- progressive enhancement
  {
    const page = await browser.newPage();
    await page.setJavaScriptEnabled(false);
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    const nojs = await page.evaluate(() => ({
      navVisible: !!document.querySelector(".nav-list") &&
        getComputedStyle(document.querySelector(".nav-list")).display !== "none",
      navItems: document.querySelectorAll(".nav-list a").length,
      toggleShown: (() => {
        const t = document.querySelector(".nav-toggle");
        return !!t && t.getBoundingClientRect().width > 0;
      })(),
      mainText: document.querySelector("main").textContent.trim().length,
    }));
    check(nojs.navVisible && nojs.navItems === 6,
      "JS disabled: full nav is visible without the toggle", JSON.stringify(nojs));
    check(!nojs.toggleShown, "JS disabled: the nav toggle stays hidden", JSON.stringify(nojs));
    fs.writeFileSync(path.join(OUT, "progressive-enhancement.json"), JSON.stringify(nojs, null, 2));
    await page.close();
  }

  // ---------------------------------------------------------------- mobile nav control
  {
    const page = await browser.newPage();
    await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 1 });
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    const before = await page.evaluate(() => {
      const t = document.querySelector(".nav-toggle");
      const list = document.getElementById("primary-nav");
      return {
        visible: !!t && t.getBoundingClientRect().width > 0,
        tag: t ? t.tagName : null,
        role: t ? t.getAttribute("aria-controls") : null,
        expanded: t ? t.getAttribute("aria-expanded") : null,
        listRendered: list ? list.getBoundingClientRect().height > 0 : null,
      };
    });
    check(before.visible && before.tag === "BUTTON" && before.role === "primary-nav",
      "mobile nav control is a real <button> with aria-controls (ES5 screen)",
      JSON.stringify(before));
    await page.evaluate(() => document.querySelector(".nav-toggle").focus());
    await page.keyboard.press("Enter");
    await new Promise((r) => setTimeout(r, 120));
    const opened = await page.evaluate(() => {
      const t = document.querySelector(".nav-toggle");
      const list = document.getElementById("primary-nav");
      return { expanded: t.getAttribute("aria-expanded"),
        listRendered: list.getBoundingClientRect().height > 0,
        linkVisible: [...list.querySelectorAll("a")].every((a) => a.getBoundingClientRect().width > 0) };
    });
    check(opened.expanded === "true" && opened.listRendered && opened.linkVisible,
      "keyboard: Enter on the nav control expands the nav (aria-expanded=true)",
      JSON.stringify(opened));
    await page.keyboard.press("Escape");
    await new Promise((r) => setTimeout(r, 120));
    const closed = await page.evaluate(() => ({
      expanded: document.querySelector(".nav-toggle").getAttribute("aria-expanded"),
      focusIsToggle: document.activeElement === document.querySelector(".nav-toggle"),
      listRendered: document.getElementById("primary-nav").getBoundingClientRect().height > 0,
    }));
    check(closed.expanded === "false" && !closed.listRendered && closed.focusIsToggle,
      "keyboard: Escape collapses the nav and returns focus to the control",
      JSON.stringify(closed));
    fs.writeFileSync(path.join(OUT, "mobile-nav.json"),
      JSON.stringify({ before, opened, closed }, null, 2));
    await page.close();
  }

  // ---------------------------------------------------------------- below-fold rendering
  {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    const probe = await page.evaluate(async () => {
      const selectors = [".cards", ".skill-list", ".certs", ".edu-list", "#contact"];
      const before = {};
      for (const sel of selectors) {
        const el = document.querySelector(sel);
        before[sel] = el ? Math.round(el.getBoundingClientRect().height) : null;
      }
      const el = document.querySelector(".certs");
      el.scrollIntoView();
      await new Promise((r) => setTimeout(r, 200));
      const after = {};
      for (const sel of selectors) {
        const node = document.querySelector(sel);
        after[sel] = node ? Math.round(node.getBoundingClientRect().height) : null;
      }
      return { before, after };
    });
    const ok = Object.values(probe.after).every((h) => h !== null && h > 0);
    check(ok, "below-fold sections render (content-visibility does not hide content)",
      JSON.stringify(probe));
    fs.writeFileSync(path.join(OUT, "below-fold.json"), JSON.stringify(probe, null, 2));
    await page.close();
  }

  // ---------------------------------------------------------------- print (A17 / D15)
  {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    await page.emulateMediaType("print");
    const print = await page.evaluate(() => {
      const line = document.querySelector(".print-contact");
      const cs = line ? getComputedStyle(line) : null;
      const r = line ? line.getBoundingClientRect() : null;
      const body = document.querySelector("main").textContent;
      return {
        printContactVisible: !!line && cs.display !== "none" && r.top < 1123,
        printContactText: line ? line.textContent.trim() : null,
        navHidden: getComputedStyle(document.querySelector(".site-nav")).display === "none",
        toggleHidden: (() => {
          const t = document.querySelector(".nav-toggle");
          return !t || getComputedStyle(t).display === "none";
        })(),
        hasName: body.includes("Mohammed Tawfiq Rahmy"),
        hasRole: body.includes("Associate Solutions Engineer"),
        hasEmployer: body.includes("Renosystems"),
        hasLinkedinUrl: body.includes("https://www.linkedin.com/in/mohammed-rahmy") ||
          (line ? line.textContent.includes("https://www.linkedin.com/in/mohammed-rahmy") : false),
      };
    });
    check(print.printContactVisible, "print: first printed page shows a readable contact line",
      JSON.stringify(print));
    check(print.navHidden && print.toggleHidden,
      "print: interactive-only affordances are not printed", JSON.stringify(print));
    const pdfPath = path.join(OUT, "print", "index.pdf");
    await page.pdf({ path: pdfPath, format: "a4", printBackground: true });
    fs.writeFileSync(path.join(OUT, "print.json"), JSON.stringify(print, null, 2));
    check(fs.existsSync(pdfPath) && fs.statSync(pdfPath).size > 5000,
      "print: PDF render produced", `size=${fs.existsSync(pdfPath) ? fs.statSync(pdfPath).size : 0}`);
    // second artefact: a printed project page (detail pages print the same chrome)
    const p2 = await browser.newPage();
    await p2.setViewport({ width: 1280, height: 900 });
    await p2.goto(`${origin}/projects/sama-soc-triage.html`, { waitUntil: "load" });
    await p2.emulateMediaType("print");
    await p2.pdf({ path: path.join(OUT, "print", "sama-soc-triage.pdf"), format: "a4",
      printBackground: true });
    await p2.close();
    await page.close();
  }

  // ---------------------------------------------------------------- layout sanity
  {
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 1000 });
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    const order = await page.evaluate(() => ({
      h1: [...document.querySelectorAll("h1")].map((h) => h.textContent.trim()),
      headings: [...document.querySelectorAll("h1,h2,h3,h4,h5,h6")]
        .map((h) => h.tagName + ":" + h.textContent.trim().slice(0, 34)),
      landmarks: {
        header: document.querySelectorAll("header").length,
        nav: document.querySelectorAll("nav").length,
        main: document.querySelectorAll("main").length,
        footer: document.querySelectorAll("footer").length,
      },
      imgAlt: [...document.querySelectorAll("img")].map((i) => i.alt),
      photoNatural: (() => {
        const i = document.querySelector("img.portrait");
        return i ? { w: i.naturalWidth, h: i.naturalHeight, wAttr: i.getAttribute("width"),
          hAttr: i.getAttribute("height") } : null;
      })(),
    }));
    results.layout = order;
    check(order.h1.length === 1, "exactly one h1 on the index", JSON.stringify(order.h1));
    check(order.landmarks.main === 1 && order.landmarks.footer >= 1 && order.landmarks.nav >= 1,
      "semantic landmarks present (header/nav/main/footer)", JSON.stringify(order.landmarks));
    check(order.imgAlt.every((a) => a && a.trim().length > 0),
      "every image has meaningful alt text", JSON.stringify(order.imgAlt));
    check(order.photoNatural && order.photoNatural.w === 400 && order.photoNatural.h === 400 &&
      order.photoNatural.wAttr === "400" && order.photoNatural.hAttr === "400",
      "portrait loads at 400x400 with explicit width/height attributes (no layout shift)",
      JSON.stringify(order.photoNatural));
    await page.close();
  }

  await browser.close();
  server.close();

  const summary = { checks: checkCount, failures, axe: Object.fromEntries(
    Object.entries(axeSummary).map(([k, v]) => [k, {
      violations: v.violations.length,
      critical: v.violations.filter((x) => x.impact === "critical").length,
      serious: v.violations.filter((x) => x.impact === "serious").length,
      moderate: v.violations.filter((x) => x.impact === "moderate").length,
      minor: v.violations.filter((x) => x.impact === "minor").length,
      passes: v.passes,
    }])) };
  fs.writeFileSync(path.join(OUT, "browser-summary.json"), JSON.stringify(summary, null, 2));
  console.log("\n" + "=".repeat(78));
  console.log(`browser checks run: ${checkCount}   failures: ${failures.length}`);
  failures.forEach((f) => console.log("  FAILED: " + f));
  console.log("BROWSER CHECKS RESULT: " + (failures.length ? "FAIL" : "PASS"));
  console.log("=".repeat(78));
  process.exit(failures.length ? 1 : 0);
}

main().catch((err) => {
  console.error("BROWSER CHECKS CRASHED:", err);
  process.exit(2);
});
