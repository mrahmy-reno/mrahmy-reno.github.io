#!/usr/bin/env python3
"""B1-05 regression tests — one test per defect repaired in this card (B1-04 register).

Every test is written so that it would have FAILED on the pre-repair revision
(95caf76b1a024d04535bc51e6c65e47a868313b4) and PASSES only when the repair is in place.

Python-stdlib only and no node_modules needed, so this runs in a fresh clone: it exercises the
delivery tooling itself inside a throwaway `git clone` of this repository (a clone contains only
committed files, which is precisely the "fresh clone" the A11 criterion is about).

Covered:
  D-01  tools/install_dev_tooling.sh (and tools/make_assets.sh) must act on the checkout they are
        run from, never on a hardcoded authoring path.
  D-02  the documented check suite must degrade HONESTLY in a clone without node_modules: the
        Node-dependent steps are reported SKIPPED with a remedy, and the run still exits non-zero.
  D-03  the rendered-text extractor must prove it reached the LAST section (content-visibility
        hazard) before a dump is trusted downstream.
  D-04  regenerating the site must leave the working tree clean (no tracked bytecode).
  D-06  the suite summary must report the MEDIAN of the kept Lighthouse runs, not one run.

Run: python3 tests/regression_repairs.py        (also step 02b of tests/run_all.sh)
Exit 0 = every regression test passed.
"""
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
RESULTS = []
TMP: str = ""


def check(cond, label, detail=""):
    RESULTS.append((bool(cond), label))
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""))
    return bool(cond)


def run(cmd, cwd=None, env=None, timeout=900):
    return subprocess.run(cmd, cwd=cwd, env=env, timeout=timeout,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


# ---------------------------------------------------------------------------- fresh clone helper
def fresh_clone(name="clone"):
    dest = pathlib.Path(TMP) / name
    r = run(["git", "clone", "--quiet", str(REPO), str(dest)])
    if r.returncode != 0:
        check(False, f"git clone of {REPO} succeeded", r.stdout.strip()[:400])
        sys.exit(1)
    return dest


def stub_dir(names):
    """A temp bin dir holding stub executables that record the cwd they were called from."""
    d = pathlib.Path(TMP) / "stub-bin"
    d.mkdir(exist_ok=True)
    for n in names:
        p = d / n
        p.write_text("#!/usr/bin/env bash\n"
                     f'echo "STUB-{n.upper()} cwd=$(pwd)"\n'
                     f'echo "STUB-{n.upper()} argv=$*"\n'
                     "exit 0\n")
        p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return d


# ------------------------------------------------------------------------- D-01: location-independence
def test_d01_install_script_uses_its_own_checkout():
    clone = fresh_clone("clone-d01")
    stub = stub_dir(["npm"])
    env = dict(os.environ)
    env["PATH"] = f"{stub}:{env.get('PATH', '')}"
    r = run(["bash", "tools/install_dev_tooling.sh"], cwd=clone, env=env)
    marker = f"STUB-NPM cwd={clone}"
    check(r.returncode == 0, "D-01 install script exits 0 with a stubbed npm",
          f"exit={r.returncode}")
    check(marker in r.stdout,
          "D-01 install script runs npm in the checkout it was invoked from (not the authoring path)",
          f"expected {marker!r}; output={r.stdout.strip()[:300]}")
    check(str(REPO) not in r.stdout,
          "D-01 install script does not touch the authoring workspace",
          f"output={r.stdout.strip()[:300]}")


def test_d01_no_tooling_script_hardcodes_an_absolute_path():
    offenders = []
    for script in sorted((REPO / "tools").glob("*.sh")):
        for i, line in enumerate(script.read_text().splitlines(), 1):
            if re.match(r"^\s*cd\s+\S", line) and "dirname" not in line:
                offenders.append(f"{script.name}:{i}: {line.strip()}")
    check(not offenders,
          "D-01 every tools/*.sh that changes directory derives it from its own location",
          "; ".join(offenders) or "no hardcoded cd")


# ------------------------------------------------------------------------------- D-02: honest skip
def test_d02_preflight_reports_missing_tooling():
    clone = fresh_clone("clone-d02")
    check(not (clone / "node_modules").exists(),
          "D-02 the fresh clone really has no node_modules (precondition of the test)")
    r = run(["bash", "tools/check_dev_tooling.sh"], cwd=clone)
    out = r.stdout
    check(r.returncode != 0,
          "D-02 preflight exits non-zero when the Node tooling is absent", f"exit={r.returncode}")
    check("PREREQUISITE MISSING" in out and "node_modules" in out,
          "D-02 preflight names the missing prerequisite", out.strip()[:300])
    check("install_dev_tooling.sh" in out,
          "D-02 preflight gives the exact remedy command", out.strip()[:300])


def test_d02_suite_reports_skipped_steps_and_still_fails():
    clone = fresh_clone("clone-d02-suite")
    script = clone / "tests/run_all.sh"
    lines = script.read_text().splitlines(keepends=True)
    kept = [ln for ln in lines if "02b_regression_repairs" not in ln]
    removed = len(lines) - len(kept)
    # Two lines carry the regression step: the `run_step` invocation and its summary row. Both are
    # dropped here - recursing into the suite from inside the suite would be an infinite regress,
    # and leaving the summary row would trip `set -u` on the now-unset REGRESSION_RC.
    check(removed >= 1 and not any("02b_regression_repairs" in ln for ln in kept),
          "D-02 run_all.sh wires the regression step (guard against drift in the suite)",
          f"removed {removed} line(s)")
    # Recursion guard: the suite must not run the suite again inside the suite.
    kept.append("# recursion guard: regression step removed by tests/regression_repairs.py\n")
    script.write_text("".join(kept))

    ev = pathlib.Path(TMP) / "clone-d02-suite-evidence"
    env = dict(os.environ)
    env["EVIDENCE_DIR"] = str(ev)
    r = run(["bash", "tests/run_all.sh"], cwd=clone, env=env, timeout=1200)
    out = r.stdout
    summary = (ev / "11_summary.txt").read_text() if (ev / "11_summary.txt").exists() else ""
    skipped_steps = ["03_browser_checks", "04_text_scans", "06_link_check", "07_html_validation",
                     "08_lighthouse"]
    check(r.returncode != 0,
          "D-02 the suite exits non-zero in a clone without tooling (no false PASS)",
          f"exit={r.returncode}")
    check(all(f"STEP {s}" in out and "SKIPPED" in out for s in skipped_steps),
          "D-02 every Node-dependent step is reported SKIPPED, none silently omitted",
          "; ".join(s for s in skipped_steps if f"STEP {s}" not in out) or "all five reported")
    check(summary.count("SKIP (node tooling missing — not run)") == len(skipped_steps),
          "D-02 the summary marks those steps SKIP instead of printing an exit code",
          summary.strip()[:400])
    check("PREREQUISITE MISSING" in out and "install_dev_tooling.sh" in out,
          "D-02 the run states the missing prerequisite and the remedy",
          out.strip()[-400:])
    check(not re.search(r"STEP (03|04|06|07|08)\w*[^\n]*exit 0", out),
          "D-02 no Node-dependent step claims exit 0 when it could not run")


# ------------------------------------------------------------------- D-03: extraction coverage guard
def test_d03_extractor_asserts_last_section_coverage():
    src = (REPO / "tests" / "browser_checks.mjs").read_text()
    check("lastMarker" in src and "reaches the last section" in src,
          "D-03 browser_checks asserts a marker from the LAST section is present in the dump")
    check("createTreeWalker(last" in src,
          "D-03 the coverage marker is read from the last section itself (not a fixed string)")
    styles = (REPO / "docs" / "assets" / "styles.css").read_text()
    check("content-visibility: auto" in styles,
          "D-03 the hazard being guarded still exists in styles.css (guard is not dead code)")


# ----------------------------------------------------------------- D-04: reproducible working tree
def test_d04_regeneration_leaves_the_tree_clean():
    clone = fresh_clone("clone-d04")
    r = run(["python3", "tools/build_site.py"], cwd=clone)
    check(r.returncode == 0, "D-04 the documented build succeeds in a fresh clone",
          f"exit={r.returncode} {r.stdout.strip()[:200]}")
    st = run(["git", "status", "--porcelain"], cwd=clone).stdout.strip()
    check(st == "", "D-04 regeneration leaves the fresh clone byte-identical (git status clean)",
          st[:300] or "clean")
    tracked = run(["git", "ls-files"], cwd=clone).stdout
    pyc = [ln for ln in tracked.splitlines() if ln.endswith(".pyc") or "__pycache__" in ln]
    check(not pyc, "D-04 no Python bytecode is tracked in the repository", "; ".join(pyc))
    check("__pycache__/" in (REPO / ".gitignore").read_text(),
          "D-04 .gitignore excludes __pycache__/")


# ------------------------------------------------------------------------- D-06: median reporting
def _lh_json(perf, acc=100, bp=100, seo=100):
    return json.dumps({"categories": {
        "performance": {"score": perf / 100},
        "accessibility": {"score": acc / 100},
        "best-practices": {"score": bp / 100},
        "seo": {"score": seo / 100},
    }})


def test_d06_summary_reports_the_median_run():
    d = pathlib.Path(TMP) / "lh"
    d.mkdir(exist_ok=True)
    for i, perf in enumerate([99, 100, 100], start=1):
        (d / f"lighthouse-index-run{i}.json").write_text(_lh_json(perf))
    files = sorted(str(p) for p in d.glob("lighthouse-index-run*.json"))
    r = run(["python3", "tools/lh_median.py", *files])
    check(r.returncode == 0, "D-06 median helper exits 0 when every median clears the A5 bar",
          f"exit={r.returncode}")
    check("performance" in r.stdout and "median=100" in r.stdout and "99,100,100" in r.stdout,
          "D-06 summary reports the MEDIAN (100) of runs 99/100/100, not the first run",
          r.stdout.strip().replace("\n", " | ")[:400])
    # a genuine dip must still be reported and must still fail the bar
    (d / "lighthouse-index-run4.json").write_text(_lh_json(60))
    files = sorted(str(p) for p in d.glob("lighthouse-index-run*.json"))
    r2 = run(["python3", "tools/lh_median.py", *files])
    check("median=99" in r2.stdout and "BELOW THRESHOLD" not in r2.stdout,
          "D-06 one bad run among good ones is kept visible without failing the median",
          r2.stdout.strip().replace("\n", " | ")[:400])
    d2 = pathlib.Path(TMP) / "lh-fail"
    d2.mkdir(exist_ok=True)
    for i, perf in enumerate([60, 55, 62], start=1):
        (d2 / f"lighthouse-index-run{i}.json").write_text(_lh_json(perf))
    files2 = sorted(str(p) for p in d2.glob("lighthouse-index-run*.json"))
    r3 = run(["python3", "tools/lh_median.py", *files2])
    check(r3.returncode != 0 and "BELOW THRESHOLD" in r3.stdout,
          "D-06 the A5 bar is still enforced on the median (a real dip fails)",
          f"exit={r3.returncode} {r3.stdout.strip().replace(chr(10), ' | ')[:300]}")
    run_all = (REPO / "tests" / "run_all.sh").read_text()
    check("lh_median.py" in run_all and "run1.json" not in run_all,
          "D-06 the suite summary uses the median helper, not the first run's JSON")


def main():
    global TMP
    TMP = tempfile.mkdtemp(prefix="b1-05-regression.")
    print(f"repo    : {REPO}")
    print(f"scratch : {TMP}")
    print()
    try:
        test_d01_install_script_uses_its_own_checkout()
        test_d01_no_tooling_script_hardcodes_an_absolute_path()
        test_d03_extractor_asserts_last_section_coverage()
        test_d04_regeneration_leaves_the_tree_clean()
        test_d06_summary_reports_the_median_run()
        test_d02_preflight_reports_missing_tooling()
        test_d02_suite_reports_skipped_steps_and_still_fails()
    finally:
        summary = {"tests": len(RESULTS), "failures": [lbl for ok, lbl in RESULTS if not ok]}
        summary_path = pathlib.Path(os.environ.get("REGRESSION_SUMMARY", TMP)) / "regression-summary.json"
        try:
            summary_path.write_text(json.dumps(summary, indent=2))
        except OSError:
            pass
        print()
        print(f"regression tests: {summary['tests']}  failures: {len(summary['failures'])}")
        if summary["failures"]:
            for f in summary["failures"]:
                print(f"  FAILED: {f}")
            print("REGRESSION RESULT: FAIL")
            print(f"scratch kept for inspection: {TMP}")
            return 1
        shutil.rmtree(TMP, ignore_errors=True)
        print("REGRESSION RESULT: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
