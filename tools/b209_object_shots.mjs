/**
 * B2-09 evidence — screenshots of the NEW evidence objects at the three widths the card names
 * (390 / 768 / 1366), including the mobile breakpoint that failed N2.
 *
 * For each target page it crops a screenshot to the artefact figures that carry the new objects,
 * so the reviewer sees the object itself rather than the whole page.
 *
 *   node tools/b209_object_shots.mjs --docs docs --port 8141 --out <dir>
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
const PORT = Number(args.get("port") || 8141);
const OUT = path.resolve(args.get("out") || "/tmp/b209-objects");

const MIME = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ttf": "font/ttf",
  ".xml": "application/xml", ".txt": "text/plain" };

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

const TARGETS = [
  ["index", "index.html", 1],
  ["sama-soc-triage", "projects/sama-soc-triage.html", 1],
  ["smartops-soc-app", "projects/smartops-soc-app.html", 1],
  ["milo-ai-employee", "projects/milo-ai-employee.html", 1],
  ["pulsesec", "projects/pulsesec.html", 1],
];
const WIDTHS = [390, 768, 1366];

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  await new Promise((r) => server.listen(PORT, "127.0.0.1", r));
  const origin = `http://127.0.0.1:${PORT}`;
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  const page = await browser.newPage();
  const report = [];
  for (const [name, rel] of TARGETS) {
    await page.goto(`${origin}/${rel}`, { waitUntil: "load" });
    await new Promise((r) => setTimeout(r, 300));
    for (const w of WIDTHS) {
      await page.setViewport({ width: w, height: 900, deviceScaleFactor: 1 });
      await new Promise((r) => setTimeout(r, 250));
      // reveal every figure (the reveal transition animates opacity only) and force layout
      await page.evaluate(() => {
        for (const el of document.querySelectorAll("[data-reveal]")) el.setAttribute("data-reveal", "on");
        window.dispatchEvent(new Event("scroll"));
        document.querySelectorAll("section").forEach((s) => {
          s.style.contentVisibility = "visible"; s.style.containIntrinsicSize = "none";
        });
      });
      await new Promise((r) => setTimeout(r, 250));
      const boxes = await page.evaluate(() => {
        const figs = [...document.querySelectorAll("figure.artefact")];
        return figs.map((f, i) => {
          const r = f.getBoundingClientRect();
          const svgs = [...f.querySelectorAll("svg")];
          const shown = svgs.filter((s) => getComputedStyle(s).display !== "none");
          const shownKind = shown.map((s) => ({
            shape: s.querySelectorAll(".dg-shape").length,
            box: s.querySelectorAll(".dg-box").length,
            signal: s.querySelectorAll(".dg-signal").length,
            text: s.querySelectorAll("text").length,
          }));
          return { i, top: Math.round(r.top + window.scrollY), height: Math.round(r.height),
            shownVariants: shown.length, shownKind };
        });
      });
      for (const b of boxes) {
        const file = path.join(OUT, `${name}__${w}__fig${b.i}.png`);
        await page.screenshot({
          path: file,
          clip: { x: 0, y: Math.max(0, b.top - 8), width: w, height: Math.min(b.height + 24, 4000) },
          fullPage: true,
        });
        report.push({ page: name, width: w, figure: b.i, ...b, file });
      }
    }
  }
  fs.writeFileSync(path.join(OUT, "objects.json"), JSON.stringify(report, null, 2));
  console.log(`wrote ${report.length} object screenshots into ${OUT}`);
  for (const r of report) {
    console.log(`  ${r.page}@${r.width} fig${r.figure}: variants=${r.shownVariants} ` +
      JSON.stringify(r.shownKind));
  }
  await browser.close();
  server.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
