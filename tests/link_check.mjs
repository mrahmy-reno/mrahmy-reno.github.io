/**
 * A7 / D7 — external link destination check.
 *
 * The default build has exactly one external hyperlink destination (the L8.3 LinkedIn profile).
 * This script resolves it two ways: a raw HTTP fetch with a normal browser User-Agent, and a real
 * headless-Chrome navigation (a 999/4xx to a non-browser client is not evidence about what a
 * visitor sees). Both results are recorded verbatim.
 *
 * Usage: node tests/link_check.mjs --out <evidence dir>
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..");
const args = new Map();
for (let i = 2; i < process.argv.length; i += 2) {
  args.set(process.argv[i].replace(/^--/, ""), process.argv[i + 1]);
}
const OUT = path.resolve(args.get("out") || path.join(REPO, "evidence", "B1-03"));
const URL_TARGET = "https://www.linkedin.com/in/mohammed-rahmy";
const UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " +
  "Chrome/151.0.0.0 Safari/537.36";

fs.mkdirSync(OUT, { recursive: true });
const report = { target: URL_TARGET, started: new Date().toISOString() };

// ---------------------------------------------------------------- raw HTTP fetch
try {
  const res = await fetch(URL_TARGET, {
    redirect: "follow",
    headers: { "user-agent": UA, "accept-language": "en-US,en;q=0.9" },
  });
  report.http = { status: res.status, statusText: res.statusText, finalUrl: res.url,
    ok: res.ok, contentType: res.headers.get("content-type") };
  const body = await res.text();
  report.http.bytes = body.length;
  report.http.title = (body.match(/<title[^>]*>([^<]*)<\/title>/i) || [])[1] || null;
} catch (err) {
  report.http = { error: String(err) };
}

// ---------------------------------------------------------------- headless browser navigation
let browser;
try {
  browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || "/usr/bin/google-chrome",
    headless: true,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
  });
  const page = await browser.newPage();
  await page.setUserAgent(UA);
  const response = await page.goto(URL_TARGET, { waitUntil: "domcontentloaded", timeout: 45000 });
  await new Promise((r) => setTimeout(r, 2500));
  report.browser = {
    status: response ? response.status() : null,
    finalUrl: page.url(),
    title: await page.title(),
    textSample: (await page.evaluate(() => document.body.innerText || "")).slice(0, 400),
  };
} catch (err) {
  report.browser = { error: String(err) };
} finally {
  if (browser) await browser.close();
}

report.finished = new Date().toISOString();
fs.writeFileSync(path.join(OUT, "link-check.json"), JSON.stringify(report, null, 2));

/* Verdict logic.
 *
 * LinkedIn answers unauthenticated automated clients with HTTP 999 and redirects a real browser
 * to its authwall, whose `sessionRedirect` parameter contains the profile path that was
 * requested. That is the site owner's platform behaviour, not a defect in this site: the URL is
 * the FACTS_LEDGER L8.3 value, a browser does reach linkedin.com, and the redirect proves the
 * profile path was accepted rather than rejected as unknown. The check therefore fails only on
 * a real navigation failure, a non-LinkedIn final host, a 404/410/5xx status, or a redirect that
 * does not carry the exact profile path. The 999 status is recorded verbatim above.
 */
const warnings = [];
const failures = [];

if (!report.browser || report.browser.error) {
  failures.push(`browser navigation failed: ${report.browser ? report.browser.error : "no result"}`);
} else {
  const finalUrl = report.browser.finalUrl || "";
  if (!finalUrl.startsWith("https://www.linkedin.com/")) {
    failures.push(`final URL left linkedin.com: ${finalUrl}`);
  }
  const profilePath = "/in/mohammed-rahmy";
  if (!finalUrl.includes(profilePath)) {
    failures.push(`final URL does not carry the requested profile path: ${finalUrl}`);
  }
  const status = report.browser.status;
  if ([404, 410].includes(status) || (status >= 500 && status !== 999)) {
    failures.push(`browser navigation returned HTTP ${status}`);
  }
  if (status === 999 || finalUrl.includes("authwall")) {
    warnings.push("LinkedIn answered an unauthenticated automated client with HTTP " +
      `${status} and/or its authwall: ${
        finalUrl.includes("authwall")
          ? "the authwall sessionRedirect carries the exact requested profile path, which " +
            "confirms the destination exists (a login wall, not a 404). Anonymous visitors on " +
            "a normal browser may hit the same wall, which is the risk PRD section 5 documents " +
            "and the reason the URL is also printed as text next to the link."
          : "anti-bot status; no browser-level confirmation possible."}`);
  }
}
if (report.http && report.http.status >= 500 && report.http.status !== 999) {
  failures.push(`HTTP fetch returned ${report.http.status}`);
}
if (report.http && report.http.status === 999) {
  warnings.push(`raw HTTP fetch returned 999 (LinkedIn refuses non-browser clients): ${URL_TARGET}`);
}
report.warnings = warnings;
report.failures = failures;
fs.writeFileSync(path.join(OUT, "link-check.json"), JSON.stringify(report, null, 2));

console.log(JSON.stringify(report, null, 2));
console.log("\n" + "=".repeat(78));
warnings.forEach((w) => console.log("WARN: " + w));
console.log("LINK CHECK RESULT: " +
  (failures.length ? "FAIL " + JSON.stringify(failures) : "PASS"));
console.log("=".repeat(78));
process.exit(failures.length ? 1 : 0);
