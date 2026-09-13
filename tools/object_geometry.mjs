/**
 * P1/P2 — rendered-box geometry of every displayed artefact.
 *
 * WHY THIS EXISTS. `tests/design_checks.py` asserts the *markup* of an artefact (SVG class names:
 * `dg-shape >= 1`, `dg-box = 0`). `tools/b209_object_shots.mjs` recorded each figure's HEIGHT but
 * never its WIDTH and screenshotted it with a full-viewport-wide clip, so an object squeezed into
 * the 138 px rail of the A5 register grid screenshotted as a strip of whitespace and was certified
 * as delivered. The object shipped at 138 x 30 px on every desktop width (B2-10 P1).
 *
 * This tool measures the RENDERED BOX of every `figure.artefact` and of the SVG variant actually
 * displayed, at the widths the layout switches at, and reports the container chain so a figure that
 * is a bare grid child (rather than a descendant of the layout's body column) is visible in the
 * data. It also measures the rendered size of the diagram label text, which is what "legible"
 * actually means for a drawn code surface.
 *
 * It is read-only against the served tree; it never writes into `docs/`.
 *
 *   node tools/object_geometry.mjs --docs docs --out <dir> [--port 8147] [--crops] [--widths 768,1024,1440]
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
const DOCS = path.resolve(args.get("docs") || path.join(REPO, "docs"));
const PORT = Number(args.get("port") || 8147);
const OUT = path.resolve(args.get("out") || "/tmp/object-geometry");
const WANT_CROPS = args.has("crops");
const WIDTHS = (args.get("widths") || "768,1024,1440").split(",").map(Number);

const MIME = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ttf": "font/ttf",
  ".xml": "application/xml", ".txt": "text/plain", ".woff2": "font/woff2" };

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]);
  if (p.endsWith("/")) p += "index.html";
  const file = path.join(DOCS, p);
  if (!file.startsWith(DOCS) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end("not found"); return;
  }
  res.writeHead(200, { "Content-Type": MIME[path.extname(file)] || "application/octet-stream" });
  fs.createReadStream(file).pipe(res);
});

const SLUGS = ["sama-soc-triage", "smartops-soc-app", "milo-ai-employee", "pulsesec",
  "tonsy-gpt", "smart-care", "halalbot", "forwheelz", "email-mcp", "voice-agent-core"];
const PAGES = ["index.html", ...SLUGS.map((s) => `projects/${s}.html`), "404.html"];

/** Runs in the page. Returns one record per displayed `figure.artefact`. */
function probe() {
  const px = (v) => Math.round(v * 100) / 100;
  const visible = (el) => el.getBoundingClientRect().width > 1
    && getComputedStyle(el).display !== "none";
  const out = [];
  for (const fig of document.querySelectorAll("figure.artefact, figure.system-map")) {
    const svgs = [...fig.querySelectorAll("svg")];
    const shown = svgs.filter(visible);
    const svg = shown[0] || null;
    const fr = fig.getBoundingClientRect();
    const sr = svg ? svg.getBoundingClientRect() : null;
    // container chain, up to the plane's wrap
    const chain = [];
    for (let el = fig.parentElement; el && chain.length < 6
        && !el.classList.contains("wrap"); el = el.parentElement) {
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      chain.push({ tag: el.tagName, cls: el.className || null,
        display: cs.display, cols: cs.gridTemplateColumns,
        width: px(r.width) });
    }
    // the box the layout actually gives the figure's content column
    const parent = fig.parentElement;
    const pHave = parent ? getComputedStyle(parent) : null;
    const containerCols = parent && pHave && pHave.display.includes("grid")
      ? pHave.gridTemplateColumns.split(" ").map(parseFloat) : null;
    // legibility of the drawn label text: declared SVG user-unit size x the render scale
    let labelDeclared = null;
    let labelRendered = null;
    let shapeRows = null;
    if (svg) {
      const t = svg.querySelector("text");
      if (t) {
        labelDeclared = px(parseFloat(getComputedStyle(t).fontSize));
        const vb = (svg.getAttribute("viewBox") || "").split(/\s+/).map(Number);
        if (vb.length === 4 && vb[2] > 0 && sr) labelRendered = px(labelDeclared * (sr.width / vb[2]));
      }
      const shape = svg.querySelector(".dg-shape");
      if (shape) {
        // the field rows of a code surface are the text elements bound inside the panel
        const sx = parseFloat(shape.getAttribute("x") || 0);
        const sw = parseFloat(shape.getAttribute("width") || 0);
        shapeRows = [...svg.querySelectorAll("text")].filter((n) => {
          const x = parseFloat(n.getAttribute("x") || NaN);
          return Number.isFinite(x) && x >= sx && x <= sx + sw;
        }).length;
      }
    }
    out.push({
      label: (fig.querySelector("figcaption")?.textContent || "").trim().slice(0, 60),
      figure: { w: px(fr.width), h: px(fr.height) },
      svg: sr ? { w: px(sr.width), h: px(sr.height), viewBox: svg.getAttribute("viewBox"),
        cls: svg.getAttribute("class") } : null,
      shownVariants: shown.length,
      parentTag: parent ? parent.tagName : null,
      parentClass: parent ? parent.className : null,
      parentDisplay: pHave ? pHave.display : null,
      containerCols,
      chain,
      labelDeclaredPx: labelDeclared,
      labelRenderedPx: labelRendered,
      shapeRows,
    });
  }
  return out;
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  await new Promise((r) => server.listen(PORT, "127.0.0.1", r));
  const origin = `http://127.0.0.1:${PORT}`;
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  const page = await browser.newPage();
  const report = {};
  for (const rel of PAGES) {
    await page.goto(`${origin}/${rel}`, { waitUntil: "load" });
    await new Promise((r) => setTimeout(r, 250));
    report[rel] = {};
    for (const w of WIDTHS) {
      await page.setViewport({ width: w, height: 900, deviceScaleFactor: 1 });
      await new Promise((r) => setTimeout(r, 220));
      await page.evaluate(() => {
        // The shipped reveal is `html.js [data-reveal] { opacity: 0 }` + `.is-in { opacity: 1 }`,
        // set by an IntersectionObserver. A figure far below the fold never intersects, so a crop
        // taken without this would be a blank rectangle. Mirror the shipped JS and then belt-and-
        // braces with an inline style, so the screenshot shows the object a visitor sees.
        for (const el of document.querySelectorAll("[data-reveal]")) {
          el.classList.add("is-in");
          el.style.opacity = "1";
          el.style.transform = "none";
        }
        document.querySelectorAll("section").forEach((s) => {
          s.style.contentVisibility = "visible"; s.style.containIntrinsicSize = "none";
        });
      });
      await new Promise((r) => setTimeout(r, 200));
      report[rel][`${w}`] = await page.evaluate(probe);
      if (WANT_CROPS) {
        // crop to the FIGURE's own box (the whole point: the pre-fix helper clipped the full
        // viewport width, so a 138 px object sat in a strip of whitespace)
        const boxes = await page.evaluate(() => [...document.querySelectorAll("figure.artefact, figure.system-map")]
          .map((f) => { const r = f.getBoundingClientRect();
            return { top: Math.round(r.top + window.scrollY), left: Math.round(r.left),
              width: Math.round(r.width), height: Math.round(r.height) }; }));
        const slug = rel.replace(/\.html$/, "").replace(/\//g, "_");
        for (let i = 0; i < boxes.length; i += 1) {
          const b = boxes[i];
          if (b.width < 2 || b.height < 2) continue;
          await page.screenshot({
            path: path.join(OUT, `${slug}__${w}__fig${i}.png`),
            captureBeyondViewport: true,
            clip: { x: Math.max(0, b.left - 10), y: Math.max(0, b.top - 10),
              width: Math.min(b.width + 20, 2200), height: Math.min(b.height + 20, 4000) },
          });
        }
      }
    }
  }
  fs.writeFileSync(path.join(OUT, "object-geometry.json"), JSON.stringify(report, null, 2));
  let n = 0;
  let worst = null;
  for (const [rel, byW] of Object.entries(report)) {
    for (const [w, figs] of Object.entries(byW)) {
      for (const f of figs) {
        if (!f.svg) continue;
        n += 1;
        if (worst === null || f.svg.w < worst.svgW) worst = { rel, w, svgW: f.svg.w };
        console.log(`${rel}@${w}  fig "${f.label.slice(0, 34)}"  frame=${f.figure.w}x${f.figure.h}`
          + `  svg=${f.svg.w}x${f.svg.h}  labelRendered=${f.labelRenderedPx}px`
          + `  parent=${f.parentTag}.${f.parentClass}  rows=${f.shapeRows}`);
      }
    }
  }
  console.log(`\nmeasured ${n} displayed artefact boxes across ${Object.keys(report).length} pages`);
  console.log(`narrowest displayed SVG: ${JSON.stringify(worst)}`);
  if (WANT_CROPS) console.log(`crops written into ${OUT}`);
  await browser.close();
  server.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
