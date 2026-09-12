// Prints resolved test-tooling versions (reproducibility record for A11/D9).
const mods = ["puppeteer-core", "axe-core", "@axe-core/puppeteer", "html-validate", "lighthouse"];
const out = {};
for (const m of mods) {
  try {
    out[m] = require(m + "/package.json").version;
  } catch (e) {
    out[m] = "ERROR: " + e.message;
  }
}
console.log(JSON.stringify(out, null, 2));
