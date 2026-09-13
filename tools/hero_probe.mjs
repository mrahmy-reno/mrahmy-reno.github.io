/**
 * B2-11 / hero item — measure the first screen's object order, so the "fix it or record a
 * programme decision" call rests on numbers rather than taste.
 *
 * Reports, at the shipped breakpoints, the y-order and rendered boxes of the hero's parts: the
 * eyebrow, the h1, the claim, the six-row attributes table (.glance-strip), the point of view
 * (.band-statement), the portrait and the CTA row — plus what is inside the first viewport at zero
 * scroll, and how much vertical space the attributes table takes before the point of view starts.
 *
 * Read-only against the served tree.
 *
 *   node hero_probe.mjs --docs docs --out hero_probe.json [--port 8151]
 */
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import puppeteer from "puppeteer-core";

const args = new Map();
for (let i = 2; i < process.argv.length; i += 2) {
  args.set(process.argv[i].replace(/^--/, ""), process.argv[i + 1]);
}
const DOCS = path.resolve(args.get("docs") || "docs");
const PORT = Number(args.get("port") || 8151);
const OUT = args.get("out") || "hero_probe.json";
const WIDTHS = (args.get("widths") || "390,768,1024,1366,1440").split(",").map(Number);

const MIME = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ttf": "font/ttf" };
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

const SELECTORS = [
  [".eyebrow", "eyebrow"],
  ["#hero-h1", "h1"],
  [".claim", "claim"],
  [".glance-strip", "attributes table (6 rows)"],
  [".band-statement", "point of view"],
  [".portrait", "portrait"],
  [".cta-row", "CTA row"],
];

async function main() {
  await new Promise((r) => server.listen(PORT, "127.0.0.1", r));
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
  });
  const page = await browser.newPage();
  const out = {};
  for (const w of WIDTHS) {
    for (const h of [768, 844]) {
      await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 });
      await page.goto(`http://127.0.0.1:${PORT}/index.html`, { waitUntil: "load" });
      await page.evaluate(() => {
        for (const el of document.querySelectorAll("[data-reveal]")) {
          el.classList.add("is-in"); el.style.opacity = "1"; el.style.transform = "none";
        }
      });
      await new Promise((r) => setTimeout(r, 200));
      const probe = await page.evaluate((sels) => {
        const parts = {};
        for (const [sel, label] of sels) {
          const el = document.querySelector(sel);
          if (!el) continue;
          const r = el.getBoundingClientRect();
          parts[label] = { top: Math.round(r.top + window.scrollY), bottom: Math.round(r.bottom + window.scrollY),
            left: Math.round(r.left), w: Math.round(r.width), h: Math.round(r.height),
            inFirstViewport: r.top >= 0 && r.top < window.innerHeight };
        }
        const glance = document.querySelector(".glance-strip");
        const pov = document.querySelector(".band-statement");
        const extras = {
          viewport: { w: window.innerWidth, h: window.innerHeight },
          aboveFold: Object.entries(parts).filter(([, v]) => v.inFirstViewport).map(([k]) => k),
          glanceToPovPx: (glance && pov)
            ? Math.round(pov.getBoundingClientRect().top - glance.getBoundingClientRect().bottom) : null,
          firstObjectAfterName: null,
          documentHeight: document.documentElement.scrollHeight,
        };
        // what is the first hero part below the h1, reading order?
        const heroInner = document.querySelector(".hero-inner");
        const order = [];
        (function walk(node) {
          for (const child of node.children) {
            if (child.matches && child.matches(sels.map((s) => s[0]).join(","))) {
              const r = child.getBoundingClientRect();
              order.push({ sel: child.className, top: Math.round(r.top + window.scrollY) });
            }
            walk(child);
          }
        })(heroInner || document.body);
        order.sort((a, b) => a.top - b.top);
        extras.domReadingOrderByTop = order;
        {
          const els = [...document.querySelectorAll(".hero-inner *")].filter((e) => {
            const r = e.getBoundingClientRect();
            return r.width > 20 && r.height > 8 && e.querySelectorAll(".hero-inner *").length === 0;
          });
          els.sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
          extras.firstLeafObjects = els.slice(0, 6).map((e) => ({
            tag: e.tagName, cls: e.className.toString().slice(0, 40),
            text: (e.textContent || "").trim().slice(0, 40),
            top: Math.round(e.getBoundingClientRect().top + window.scrollY),
          }));
        }
        return { parts, extras };
      }, SELECTORS);
      out[`${w}x${h}`] = probe;
    }
  }
  fs.writeFileSync(OUT, JSON.stringify(out, null, 2));
  for (const [vp, probe] of Object.entries(out)) {
    console.log(`\n=== viewport ${vp}`);
    for (const [label, v] of Object.entries(probe.parts)) {
      console.log(`  ${label.padEnd(24)} top=${String(v.top).padStart(5)} h=${String(v.h).padStart(4)}`
        + ` w=${String(v.w).padStart(4)}  ${v.inFirstViewport ? "IN FIRST VIEWPORT" : ""}`);
    }
    console.log(`  above fold: ${probe.extras.aboveFold.join(", ")}`);
    console.log(`  attributes table -> point of view gap: ${probe.extras.glanceToPovPx}px`);
    console.log(`  first leaves: ${probe.extras.firstLeafObjects.map((e) => e.text).join(" | ")}`);
  }
  await browser.close();
  server.close();
}

main().catch((e) => { console.error(e); process.exit(1); });
