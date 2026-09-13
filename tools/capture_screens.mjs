/**
 * B2-04 screenshot helper — the refusals the critic asked to be shown, not restated.
 *
 *   node tools/capture_screens.mjs --docs docs --out <dir> --port 8125
 *
 * Writes the six views that decide the repair (see evidence/B2-04/REPAIR_REPORT.md §2):
 *   index__1366x768__screen.png      the first screen: claim, point of view, one register line
 *   index__1366x768__full.png        the whole document (D1: no diagram twice; D4: length)
 *   index__1366x768__evidence.png    the "Work, shown" plane scrolled into view (D3)
 *   index__390x844__screen.png       the mobile first screen (D10 eyebrow, D2 ordinals)
 *   projects_sama__1366x768__run.png the flagship's run trace + contract excerpt
 *   index__1366x768__work.png        the project register (D2: the first ordinal)
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
const OUT = path.resolve(args.get("out") || path.join(REPO, "evidence", "B2-04"));
const PORT = Number(args.get("port") || 8125);
const CHROME = process.env.CHROME_PATH || "/usr/bin/google-chrome";
const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".ttf": "font/ttf" };

fs.mkdirSync(OUT, { recursive: true });
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

const browser = await puppeteer.launch({ executablePath: CHROME,
  args: ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"] });

async function shoot(name, url, width, height, scrollTo) {
  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  await page.goto(url, { waitUntil: "load" });
  if (scrollTo) {
    await page.evaluate((sel) => {
      const el = typeof sel === "string" ? document.querySelector(sel) : null;
      if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 40);
    }, scrollTo);
  } else {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.evaluate(() => window.scrollTo(0, 0));
  }
  await new Promise((r) => setTimeout(r, 700));      // let the reveal transitions settle
  const file = path.join(OUT, `${name}.png`);
  await page.screenshot({ path: file, fullPage: !scrollTo });
  console.log(`wrote ${file}`);
  await page.close();
}

const base = `http://127.0.0.1:${PORT}`;
await shoot("index__1366x768__screen", `${base}/index.html`, 1366, 768, "#top");
await shoot("index__1366x768__full", `${base}/index.html`, 1366, 768, null);
await shoot("index__1366x768__work", `${base}/index.html`, 1366, 768, "#projects");
await shoot("index__1366x768__evidence", `${base}/index.html`, 1366, 768, "#evidence");
await shoot("index__390x844__screen", `${base}/index.html`, 390, 844, "#top");
await shoot("projects_sama__1366x768__run", `${base}/projects/sama-soc-triage.html`, 1366, 768,
  ".diagram-panel");
await browser.close();
server.close();
