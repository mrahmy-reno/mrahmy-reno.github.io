/**
 * B2-04 measurement helper — the numbers the repair report quotes, measured from the render.
 *
 *   node tools/measure_index.mjs --docs <publish root> --port 8121 [--label before] [--json out]
 *
 * Reports, at 1366x768 and 390x844: the document height, the screens it occupies, the word count
 * of <main>, the height of every plane, the number of figures and of visible SVG text nodes, and
 * the largest diagram. Used to measure the same revision before and after the repair (see
 * evidence/B2-04/REPAIR_REPORT.md) — the "before" tree is extracted from git, so both numbers come
 * from the same script on the same host.
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
const PORT = Number(args.get("port") || 8121);
const LABEL = args.get("label") || "run";
const CHROME = process.env.CHROME_PATH || "/usr/bin/google-chrome";

const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".ttf": "font/ttf",
  ".xml": "application/xml", ".txt": "text/plain" };

const server = http.createServer((req, res) => {
  const rel = decodeURIComponent(req.url.split("?")[0]).replace(/^\//, "") || "index.html";
  const file = path.join(DOCS, rel);
  if (!file.startsWith(DOCS) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end("no"); return;
  }
  res.writeHead(200, { "content-type": MIME[path.extname(file)] || "application/octet-stream" });
  res.end(fs.readFileSync(file));
});
await new Promise((r) => server.listen(PORT, "127.0.0.1", r));

const browser = await puppeteer.launch({
  executablePath: CHROME,
  args: ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
});
const out = { label: LABEL, docs: DOCS, measured: new Date().toISOString(), viewports: {} };

for (const [w, h] of [[1366, 768], [390, 844]]) {
  const page = await browser.newPage();
  await page.setViewport({ width: w, height: h });
  await page.goto(`http://127.0.0.1:${PORT}/index.html`, { waitUntil: "load" });
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.evaluate(() => window.scrollTo(0, 0));
  const m = await page.evaluate(() => {
    const planes = [...document.querySelectorAll("section.plane")].map((s) => ({
      label: s.getAttribute("data-plane") || s.className,
      surface: s.getAttribute("data-surface"),
      height: Math.round(s.getBoundingClientRect().height),
    }));
    const figures = [...document.querySelectorAll("figure.artefact, figure.system-map")].map((f) => {
      const svgs = [...f.querySelectorAll("svg")];
      const shown = svgs.filter((s) => {
        const r = s.getBoundingClientRect();
        return r.width > 1 && r.height > 1;
      });
      return {
        figures: svgs.length,
        variantsShown: shown.length,
        height: Math.round(f.getBoundingClientRect().height),
        labels: [...f.querySelectorAll("svg text")].length,
      };
    });
    return {
      height: document.documentElement.scrollHeight,
      screens: Math.round((document.documentElement.scrollHeight / window.innerHeight) * 10) / 10,
      words: (document.querySelector("main")?.innerText || "").split(/\s+/).filter((x) => x).length,
      sections: document.querySelectorAll("section").length,
      figures: figures.length,
      figureDetail: figures,
      svgText: document.querySelectorAll("svg text").length,
      images: document.querySelectorAll("img").length,
      planes,
    };
  });
  out.viewports[`${w}x${h}`] = m;
  await page.close();
}
await browser.close();
server.close();

const lines = [`MEASURE ${LABEL}: ${DOCS}`];
for (const [vp, m] of Object.entries(out.viewports)) {
  lines.push(`  ${vp}: height=${m.height}px (${m.screens} screens) words=${m.words} `
    + `sections=${m.sections} figures=${m.figures} svgText=${m.svgText} img=${m.images}`);
  for (const p of m.planes) lines.push(`      ${String(p.label).padEnd(12)} ${p.surface.padEnd(6)} ${p.height}px`);
  for (const f of m.figureDetail) {
    lines.push(`      figure: variants=${f.figures} shown=${f.variantsShown} height=${f.height}px labels=${f.labels}`);
  }
}
console.log(lines.join("\n"));
if (args.get("json")) fs.writeFileSync(args.get("json"), JSON.stringify(out, null, 2));
