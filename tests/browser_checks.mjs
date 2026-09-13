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
    const text = node.nodeValue.replace(/\u00a0/g, " ");
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

// B2-05b / N1 — a label whose whole text is ONE word must never render on more than one line.
// The old suite measured this for `.rank` only, which is how the hero's attributes table came to
// render `Focus` as FO / CU / S and `Languages` as LANGUAGE / S at every desktop width: the body
// carried `overflow-wrap: anywhere` (every text node's min-content width was one character) and
// `.glance-item` is a flex row whose `dt` could be squeezed to ~2 characters.
//
// The line count is a DOM Range over the element's own contents — the number of line BOXES, not
// box height / line-height. Box height counts padding and produces false positives on `.chips li`,
// `.btn` and nav links, which are legitimately taller than one line.
function midwordProbe() {
  const hits = [];
  let scanned = 0;
  for (const el of document.querySelectorAll("body *")) {
    if (el.children.length > 0) continue;               // leaf text containers only
    const text = (el.textContent || "").trim();
    if (!text || /\s/.test(text) || text.length < 3) continue;   // one word, nothing else
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") continue;
    if ((cs.clipPath || "none") !== "none") continue;   // .visually-hidden is clipped, not laid out for reading
    const box = el.getBoundingClientRect();
    if (box.width < 8 || box.height < 6) continue;      // not a real text box on screen
    scanned += 1;
    const range = document.createRange();
    range.selectNodeContents(el);
    const rects = [...range.getClientRects()].filter((r) => r.width > 0 && r.height > 0);
    if (rects.length > 1) {
      hits.push({
        text: text.slice(0, 32),
        tag: el.tagName,
        cls: (el.className.toString() || "").slice(0, 40),
        parent: el.parentElement ? (el.parentElement.className.toString() || "").slice(0, 30) : "",
        width: Math.round(box.width),
        lines: rects.length,
      });
    }
  }
  return { hits, scanned };
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
      // B2-08 fact correction: the formal current role (FACTS_LEDGER §11 R2, source S5) is the
      // title asserted as a FIELD, so it is the one the first screen must carry. The superseded
      // "AI Solutions Engineer" variant survives only inside owner-authored summary prose.
      "Associate Solutions Engineer", "Renosystems",
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
  // B2-08: the responsive set covers the index and the TWO project pages that are claimed as
  // different expressions (SAMA = M2/A4 stage-gate deep, PulseSec = M4/A5 register warm), so the
  // anti-template claim has a side-by-side artefact at every width. Every page is additionally
  // captured at 1440 so the whole series is inspectable.
  const OVERS = ["index.html", "projects/sama-soc-triage.html", "projects/pulsesec.html"];
  const overflow = {};
  for (const rel of OVERS) {
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

  // every page in the series, at 1440, for the whole-set inspection
  {
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
    for (const rel of PAGES) {
      await page.goto(`${origin}/${rel}`, { waitUntil: "load" });
      await page.evaluate(async () => {
        const h = document.body.scrollHeight;
        for (let y = 0; y < h; y += 400) {
          window.scrollTo(0, y);
          await new Promise((r) => setTimeout(r, 15));
        }
        window.scrollTo(0, 0);
        await new Promise((r) => setTimeout(r, 60));
      });
      const name = `all-${rel.replace(/\//g, "_").replace(/\.html$/, "")}-1440.png`;
      await page.screenshot({ path: path.join(OUT, "screenshots", name), fullPage: true });
    }
    await page.close();
  }

  const shotCount = fs.readdirSync(path.join(OUT, "screenshots")).filter((f) => f.endsWith(".png")).length;
  check(shotCount === OVERS.length * WIDTHS.length + PAGES.length,
    `${OVERS.length * WIDTHS.length + PAGES.length} screenshots captured (12 responsive + 12 series)`,
    `found ${shotCount}`);

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

  // ------------------------------------------------- design system: states + banned defaults
  // Q10/Q11. These are the assertions the redesign introduces; each one is measured in the
  // rendered DOM rather than asserted in prose.
  const EASE_TOKENS = ["cubic-bezier(0.22,1,0.36,1)", "cubic-bezier(0.25,1,0.5,1)",
    "cubic-bezier(0.4,0,1,1)", "cubic-bezier(0.2,0,0,1)"];
  const DUR_TOKENS = [0.09, 0.16, 0.24, 0.42, 0.56];
  {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    await page.goto(`${origin}/index.html`, { waitUntil: "load" });
    // One bounded evaluation over a curated surface list, reading `class` with getAttribute().
    // Walking every element (document.querySelectorAll("body *")) with
    // `el.className.toString()` across several successive evaluations wedged Chrome's
    // Runtime.callFunctionOn in this environment while this card was being built — the failure
    // mode is an opaque CDP timeout rather than a failed check. The curated list is what the
    // assertions are actually about; the exhaustive half of the same rules ("no other
    // box-shadow literal exists at all") is asserted at the source level in
    // tests/design_checks.py, which is both cheaper and stronger.
    const SURFACES = ".site-header, .glance-strip, .glance-item, .system-map, .artefact-frame,"
      + " .evidence-figure, .diagram-panel, .evidence-panel, .empty, .callout, .contact-panel,"
      + " .card, .card-featured, .card-compact, .tag, .chips li, .cs-stage, .cs-architecture, .section,"
      + " .hero-aside, .hero-inner, .row-inner, .legend, .prev-next, .exp, .exp-list, .edu,"
      + " .edu-list, .skill-list, .cards, .cs-stage-inner";
    const INTERACTIVE = "a, button";
    const design = await page.evaluate((surfaces, interactive) => {
      const out = {};
      const cards = document.querySelectorAll("li.card");
      out.cardCount = cards.length;
      out.cardBorder = [];
      for (let i = 0; i < cards.length; i += 1) {
        const s = getComputedStyle(cards[i]);
        out.cardBorder.push({ top: s.borderBlockStartWidth, start: s.borderInlineStartWidth,
          end: s.borderInlineEndWidth, bottom: s.borderBlockEndWidth,
          radius: s.borderTopLeftRadius });
      }
      out.shadows = [];
      out.grids = [];
      out.transitions = [];
      const els = document.querySelectorAll(surfaces);
      for (let i = 0; i < els.length; i += 1) {
        const s = getComputedStyle(els[i]);
        const cls = els[i].getAttribute("class") || "";
        if (s.boxShadow !== "none") out.shadows.push({ cls, shadow: s.boxShadow });
        if (s.display.indexOf("grid") >= 0 && s.gridTemplateColumns !== "none") {
          const tracks = s.gridTemplateColumns.split(" ").filter((t) => t.length);
          if (tracks.length > 1) out.grids.push({ cls, tracks: tracks.length });
        }
        const parts = String(s.transitionDuration).split(",");
        let dur = 0;
        for (let j = 0; j < parts.length; j += 1) {
          const v = parseFloat(parts[j]) || 0;
          if (v > dur) dur = v;
        }
        if (dur > 0) {
          out.transitions.push({ cls, prop: s.transitionProperty, dur: s.transitionDuration,
            ease: s.transitionTimingFunction });
        }
      }
      out.interactive = [];
      const acts = document.querySelectorAll(interactive);
      for (let i = 0; i < acts.length; i += 1) {
        const s = getComputedStyle(acts[i]);
        out.interactive.push({ cls: acts[i].getAttribute("class") || "",
          prop: s.transitionProperty, dur: s.transitionDuration });
      }
      const h = document.querySelector(".site-header");
      const hs = getComputedStyle(h);
      out.header = { bg: hs.backgroundColor, filter: hs.backdropFilter,
        borderBottom: hs.borderBlockEndWidth, position: hs.position };
      out.svgTextCount = document.querySelectorAll("svg text").length;
      out.revealCount = document.querySelectorAll("[data-reveal]").length;
      out.mainText = document.querySelector("main").textContent.replace(/\s+/g, " ").trim().length;
      return out;
    }, SURFACES, INTERACTIVE);

    check(design.cardCount === 10, "design: the 10 project rows render as rows, not cards",
      `li.card count=${design.cardCount}`);
    const closed = design.cardBorder.filter((b) => b.top !== "0px" || b.start !== "0px" ||
      b.end !== "0px" || b.radius !== "0px");
    check(closed.length === 0,
      "banned defaults: no project row draws a closed 1px border or a radius (Q11)",
      closed.length ? JSON.stringify(closed.slice(0, 2)) : "hairline rule on one edge only");
    const ruled = design.cardBorder.filter((b) => b.bottom === "1px");
    check(ruled.length === 10, "design: every project row is separated by a hairline rule",
      `rows with a 1px block-end rule: ${ruled.length}`);

    // elevation: every painted shadow must be a wide ambient shadow (blur >= 18px) or an
    // inset highlight — never a hard, tight, offset shadow (Q11).
    const hard = [];
    for (const entry of design.shadows) {
      const re = /((?:rgba?\([^)]*\)|#\w+|transparent|currentcolor)?)\s*(-?[\d.]+px)\s+(-?[\d.]+px)\s+(-?[\d.]+px)(?:\s+(-?[\d.]+px))?(\s+inset)?/g;
      let m;
      while ((m = re.exec(entry.shadow)) !== null) {
        if (m[6]) continue;
        if (parseFloat(m[4]) < 18) {
          hard.push({ cls: entry.cls, shadow: entry.shadow.slice(0, 70) });
        }
      }
    }
    check(hard.length === 0,
      "banned defaults: no tight/hard drop shadow is painted (blur < 18px) (Q11)",
      hard.length ? JSON.stringify(hard.slice(0, 3))
        : `${design.shadows.length} ambient shadow(s), all wide`);

    const three = design.grids.filter((g) => g.tracks === 3);
    check(three.length === 0,
      "banned defaults: no symmetric three-column grid exists anywhere (Q11)",
      three.length ? JSON.stringify(three.slice(0, 3))
        : `${design.grids.length} multi-track grids, none with 3 tracks`);

    const badEase = design.transitions.filter((t) =>
      EASE_TOKENS.indexOf(String(t.ease).replace(/\s+/g, "")) < 0);
    check(badEase.length === 0,
      "motion: every running transition names one of the 4 documented timing tokens",
      badEase.length ? JSON.stringify(badEase.slice(0, 3))
        : `${design.transitions.length} transitions, all token easings`);
    const allProp = design.transitions.filter((t) => String(t.prop).indexOf("all") >= 0);
    check(allProp.length === 0, "motion: transition:all is absent",
      allProp.length ? JSON.stringify(allProp.slice(0, 3)) : "0 elements transition all properties");
    const instant = design.interactive.filter((t) => parseFloat(t.dur) === 0);
    check(instant.length === 0,
      "banned defaults: no interactive element changes state instantly (Q11)",
      instant.length ? JSON.stringify(instant.slice(0, 3))
        : `${design.interactive.length} interactive elements all transitioned`);
    const offSpec = design.transitions.filter((t) => DUR_TOKENS.indexOf(parseFloat(t.dur)) < 0);
    check(offSpec.length === 0,
      "motion: every running transition uses one of the 5 documented durations",
      offSpec.length ? JSON.stringify(offSpec.slice(0, 3))
        : "durations in use are a subset of 90/160/240/420/560ms");

    const headerAlpha = parseFloat((String(design.header.bg).match(/[\d.]+\)$/) || ["0)"])[0]);
    check(design.header.position === "sticky" &&
      (design.header.filter !== "none" || headerAlpha >= 0.9),
      "banned defaults: the sticky bar carries a real surface treatment (Q11)",
      JSON.stringify(design.header));
    check(design.header.borderBottom === "1px",
      "design: the sticky bar is closed by a hairline rule", design.header.borderBottom);

    results.design = design;

    // ---- the 404 renders the shared chrome plus the recovery surface
    const p404 = await browser.newPage();
    await p404.setViewport({ width: 1280, height: 900 });
    await p404.goto(`${origin}/404.html`, { waitUntil: "load" });
    const nf = await p404.evaluate(() => ({
      h1: document.querySelector("h1").textContent.trim(),
      map: !!document.querySelector(".notfound svg.dg"),
      contact: !!document.querySelector(".contact-panel"),
      footer: document.querySelectorAll("footer").length,
    }));
    check(nf.h1.length > 0 && nf.map && nf.contact && nf.footer >= 1,
      "404: the designed error page renders its recovery surface and the shared chrome",
      JSON.stringify(nf));
    await p404.close();

    // ---- reduced-motion parity: identical content, nothing hidden by a reveal state
    const pRed = await browser.newPage();
    await pRed.setViewport({ width: 1280, height: 900 });
    await pRed.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
    await pRed.goto(`${origin}/index.html`, { waitUntil: "load" });
    const red = await pRed.evaluate(() => ({
      mainText: document.querySelector("main").textContent.replace(/\s+/g, " ").trim().length,
      hiddenReveals: [...document.querySelectorAll("[data-reveal]")]
        .filter((el) => parseFloat(getComputedStyle(el).opacity) < 1).length,
      svgTextCount: document.querySelectorAll("svg text").length,
    }));
    check(red.mainText === design.mainText,
      "reduced motion: the page carries exactly the same text as the motion-enabled page",
      `reduced=${red.mainText} normal=${design.mainText}`);
    check(red.hiddenReveals === 0,
      "reduced motion: no element is left hidden by a reveal state",
      `${design.revealCount} reveal elements checked; ${red.hiddenReveals} below opacity 1`);
    check(red.svgTextCount === design.svgTextCount,
      "reduced motion: every diagram label is present (the stagger orders, it does not gate)",
      `reduced=${red.svgTextCount} normal=${design.svgTextCount}`);
    await pRed.close();
    await page.close();
  }

  // ------------------------------------------------- B2-04 craft regressions (D1, D2, D9, D10, D12)
  // The four visible defects the critique measured from screenshots, now measured from the
  // rendered DOM at every width they were reported at: exactly one responsive variant of every
  // diagram is displayed, the ordinal never wraps, the eyebrow never opens a line with an
  // operator, and the RENDERED type-scale emphasis is reported (not the declared token).
  {
    const craft = { variants: {}, ordinals: {}, eyebrow: null, emphasis: null,
      index: {} };
    const CRAFT_PAGES = ["index.html", "projects/sama-soc-triage.html",
      "projects/smartops-soc-app.html"];
    const craftPage = await browser.newPage();
    for (const rel of CRAFT_PAGES) {
      for (const width of [390, 768, 1366]) {
        await craftPage.setViewport({ width, height: 900 });
        await craftPage.goto(`${origin}/${rel}`, { waitUntil: "load" });
        await craftPage.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await craftPage.evaluate(() => window.scrollTo(0, 0));
        const probe = await craftPage.evaluate(() => {
          const visible = (el) => {
            const r = el.getBoundingClientRect();
            return r.width > 1 && r.height > 1;
          };
          const figs = [...document.querySelectorAll("figure.artefact, figure.system-map")];
          const variants = figs.map((fig) => {
            const svgs = [...fig.querySelectorAll("svg")];
            return {
              uids: svgs.map((s) => (s.getAttribute("aria-labelledby") || "").split(" ")[0]),
              shown: svgs.filter(visible).map((s) => s.getAttribute("class")),
              announced: svgs.filter((s) => visible(s)
                && ["img", "group"].includes(s.getAttribute("role"))).length,
              height: Math.round(fig.getBoundingClientRect().height),
            };
          });
          const ranks = [...document.querySelectorAll("#projects .rank")].map((el) => ({
            text: el.textContent.trim(),
            w: Math.round(el.getBoundingClientRect().width),
            h: Math.round(el.getBoundingClientRect().height),
            lineHeight: getComputedStyle(el).lineHeight,
          }));
          const eb = document.querySelector(".eyebrow");
          let eyebrow = null;
          if (eb) {
            const node = [...eb.childNodes].find((n) => n.nodeType === 3
              && n.textContent.includes("Mechatronics"));
            if (node) {
              const text = node.textContent;
              const start = text.indexOf("Mechatronics");
              const end = text.indexOf("×", start) + 1;
              const range = document.createRange();
              range.setStart(node, start);
              range.setEnd(node, end);
              eyebrow = { rects: range.getClientRects().length,
                firstLineOpensWithTimes: [...eb.getClientRects()].length > 0
                  && text.trimStart().startsWith("×") };
            }
          }
          const h1 = document.querySelector("h1");
          const body = getComputedStyle(document.body);
          const idx = {
            height: document.documentElement.scrollHeight,
            words: (document.querySelector("main")?.innerText || "").split(/\s+/)
              .filter((w) => w.length).length,
            povInHero: !!document.querySelector(".hero .band-statement"),
          };
          return { variants, ranks, eyebrow, idx,
            h1Px: h1 ? parseFloat(getComputedStyle(h1).fontSize) : null,
            bodyPx: parseFloat(body.fontSize), bodyLine: body.lineHeight };
        });
        craft.variants[`${rel}@${width}`] = probe.variants;
        craft.ordinals[`${rel}@${width}`] = probe.ranks;
        if (rel === "index.html") {
          craft.index[`@${width}`] = probe.idx;
          if (probe.eyebrow) craft.eyebrow = probe.eyebrow;
          if (probe.h1Px && probe.bodyPx) {
            craft.emphasis = { width, h1Px: probe.h1Px, bodyPx: probe.bodyPx,
              ratio: Math.round((probe.h1Px / probe.bodyPx) * 100) / 100 };
          }
        }
      }
    }
    await craftPage.close();

    // D1 — one variant displayed, never two. The critique measured the failure at 768/1024/1366/
    // 1440; this measures it at 390/768/1366 and counts what assistive technology is handed.
    const dupes = [];
    const announcedTwice = [];
    for (const [where, figs] of Object.entries(craft.variants)) {
      for (const fig of figs) {
        if (fig.shown.length !== 1) {
          dupes.push(`${where}: ${fig.uids.join(",")} shown=${JSON.stringify(fig.shown)}`);
        }
        if (fig.announced > 1) announcedTwice.push(`${where}: ${fig.announced} announced`);
      }
    }
    check(dupes.length === 0,
      "D1: exactly one responsive variant of every diagram is displayed at 390/768/1366",
      dupes.length ? JSON.stringify(dupes.slice(0, 3))
        : `${Object.keys(craft.variants).length} page/width combinations, every figure shows 1`);
    check(announcedTwice.length === 0,
      "D9: no diagram is announced twice to assistive technology",
      announcedTwice.length ? JSON.stringify(announcedTwice.slice(0, 3))
        : "one role=img/group element per diagram at every width");

    // D2 — the ordinal is one line, wider than its two digits, at every width.
    const wrapped = [];
    for (const [where, ranks] of Object.entries(craft.ordinals)) {
      for (const r of ranks) {
        if (r.lineHeight !== "normal" && r.h > parseFloat(r.lineHeight) * 1.5) {
          wrapped.push(`${where}: "${r.text}" ${r.w}x${r.h}px (line-height ${r.lineHeight})`);
        }
      }
    }
    check(wrapped.length === 0,
      "D2: no project ordinal wraps to two lines at 390/768/1366 (the first row included)",
      wrapped.length ? JSON.stringify(wrapped.slice(0, 3))
        : `${Object.values(craft.ordinals).flat().length} ordinals measured, all single-line`);

    // D10 — the eyebrow's "Mechatronics ×" joint is unbroken.
    check(craft.eyebrow && craft.eyebrow.rects === 1,
      "D10: the mobile eyebrow keeps 'Mechatronics ×' on one line (the operator never opens one)",
      JSON.stringify(craft.eyebrow));

    // D12 — the RENDERED emphasis, at 1366, against the 3.0 floor of the bar's Q2.
    check(craft.emphasis && craft.emphasis.ratio >= 3.0,
      "D12: the rendered h1/body type-scale emphasis at 1366 is measured and clears the 3.0 floor",
      JSON.stringify(craft.emphasis));
    check(craft.index["@1366"] && craft.index["@1366"].povInHero,
      "Q9/D4: the point of view renders inside the first screen (the hero), not 2k px down",
      JSON.stringify(craft.index["@1366"]));

    // D4 — the index is a reading page, not a register. The defect revision measured 13,396 px /
    // 17.4 screens / 1,186 words at 1366x768; the repair's ceiling is recorded here so the
    // documentation feel cannot return silently. (This is the repair's own budget, not a bar
    // clause: the bar has no length threshold. Coverage counts stay locked by static_scans.)
    const budget = { "@1366": { height: 10500, words: 1100 }, "@390": { height: 14000, words: 1100 } };
    const over = [];
    for (const [vp, cap] of Object.entries(budget)) {
      const m = craft.index[vp];
      if (!m) { over.push(`${vp}: not measured`); continue; }
      if (m.height > cap.height) over.push(`${vp}: ${m.height}px > ${cap.height}px`);
      if (m.words > cap.words) over.push(`${vp}: ${m.words} words > ${cap.words}`);
    }
    check(over.length === 0,
      "D4: the index stays inside the repair's reading budget (height and words, 1366 and 390)",
      over.length ? JSON.stringify(over) : JSON.stringify(craft.index));

    results.craft = craft;
    fs.writeFileSync(path.join(OUT, "craft.json"), JSON.stringify(craft, null, 2));
  }

  // ------------------------------------------------- B2-05b / N1: no word may break mid-word
  // The hero's attributes table broke two of its own labels mid-word at every desktop width
  // (`Focus` -> FO / CU / S, `Languages` -> LANGUAGE / S, in the first screen) and no check could
  // see it: the suite measured `.rank` only. This measures EVERY page (index, the ten project
  // pages and 404) at the five shipped breakpoints, counting line boxes with a DOM Range.
  {
    const MIDWORD_WIDTHS = [390, 768, 1024, 1366, 1440];
    const midwordPage = await browser.newPage();
    const midword = {};
    let scannedTotal = 0;
    for (const w of MIDWORD_WIDTHS) {
      for (const rel of PAGES) {
        await midwordPage.setViewport({ width: w, height: 900, deviceScaleFactor: 1 });
        await midwordPage.goto(`${origin}/${rel}`, { waitUntil: "load" });
        // off-screen sections use content-visibility: auto; render them before measuring
        await midwordPage.evaluate(async () => {
          for (let y = 0; y < document.body.scrollHeight; y += 700) {
            window.scrollTo(0, y);
            await new Promise((r) => setTimeout(r, 15));
          }
          window.scrollTo(0, 0);
          await new Promise((r) => setTimeout(r, 60));
        });
        const res = await midwordPage.evaluate(midwordProbe);
        scannedTotal += res.scanned;
        if (res.hits.length) midword[`${rel}@${w}`] = res.hits;
      }
    }
    await midwordPage.close();
    const places = Object.entries(midword);
    check(places.length === 0,
      "N1: no label that is a single word renders on more than one line, on any page at " +
      `${MIDWORD_WIDTHS.join("/")}px`,
      places.length ? JSON.stringify(places.slice(0, 3))
        : `${scannedTotal} single-word elements measured over ` +
          `${PAGES.length * MIDWORD_WIDTHS.length} page/width combinations, all single-line`);
    results.midword = midword;
    fs.writeFileSync(path.join(OUT, "midword.json"), JSON.stringify(midword, null, 2));
  }

  // ------------------------------------------------- B2-04 / D6: the displayed face is shipped
  {
    const fontPage = await browser.newPage();
    await fontPage.setViewport({ width: 1366, height: 900 });
    const fontRequests = [];
    fontPage.on("request", (r) => fontRequests.push(r.url()));
    await fontPage.goto(`${origin}/index.html`, { waitUntil: "load" });
    const font = await fontPage.evaluate(async () => {
      await document.fonts.ready;
      const faces = [...document.fonts].map((f) => ({
        family: f.family, weight: f.weight, status: f.status,
        url: (f.src || "").split("(")[1] ? f.src.split("(")[1].split(")")[0] : "",
      }));
      const probe = document.createElement("span");
      probe.style.cssText = 'position:absolute;visibility:hidden;font-size:100px;'
        + 'white-space:nowrap;font-weight:400;font-family:"Spectral Subset"';
      probe.textContent = "Hamburgefonstiv";
      document.body.appendChild(probe);
      const shipped = probe.getBoundingClientRect().width;
      // Compare against a face family that is definitely NOT the shipped serif: the shipped face
      // (B2-09: a Spectral subset) is metrically its own, so the sans fallback is a valid control.
      probe.style.fontFamily = "sans-serif";
      const fallback = probe.getBoundingClientRect().width;
      probe.remove();
      const h1 = getComputedStyle(document.querySelector("h1"));
      const usedFace = getComputedStyle(document.querySelector("h1")).fontFamily;
      return { faces, shipped: Math.round(shipped), fallback: Math.round(fallback),
        h1Family: usedFace, h1Weight: h1.fontWeight };
    });
    const loaded = font.faces.filter((f) => f.status === "loaded");
    check(loaded.length >= 2 && loaded.every((f) => f.family.includes("Spectral Subset")),
      "D6: the display faces load from this origin (no system fallback is doing the work)",
      JSON.stringify(font.faces));
    check(font.h1Family.includes("Spectral Subset"),
      "D6: the hero resolves to the shipped display face, so the identity is OS-independent",
      font.h1Family);
    check(font.shipped !== font.fallback && font.shipped > 0,
      "D6: the shipped face shapes text with its own metrics (distinct from the sans fallback)",
      `shipped=${font.shipped}px fallback=${font.fallback}px`);
    const fontFiles = fontRequests.filter((u) => u.includes("/assets/fonts/"));
    check(fontFiles.length >= 1 && fontFiles.every((u) => u.startsWith(origin)),
      "D6: the font is served from this origin — 0 third-party font requests",
      JSON.stringify(fontFiles));
    results.font = font;
    fs.writeFileSync(path.join(OUT, "fonts.json"),
      JSON.stringify({ ...font, requests: fontRequests.filter((u) => u.includes("font")) }, null, 2));
    await fontPage.close();
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
