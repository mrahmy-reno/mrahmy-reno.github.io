#!/usr/bin/env python3
"""B2-02 design checks — the mechanics the redesign introduces.

Stdlib only, no browser: it audits the *shipped* stylesheet and the *built* HTML, so it runs in
a fresh clone with no node tooling (step 02c of tests/run_all.sh). The DOM-level halves of these
assertions (computed borders, shadows, grid tracks, transition timing, reduced-motion parity) are
measured in `tests/browser_checks.mjs`, which has a real renderer.

Checks
  1. token conformance      — no raw hex / px font-size / ms / cubic-bezier() outside @layer tokens
  2. state inventory        — every state in DESIGN_SYSTEM.md §7 exists in the built CSS
  3. banned easing / reset  — no bare ease, ease-in-out, linear entrance, transition:all, outline:none
  4. motion-spec conformance— only the documented durations/easings are used, and they are tokens
  5. palette contrast       — computed per pair from the SHIPPED tokens, raw table recorded
  6. artefact audits        — label diff vs the ledger, measurement vocabulary, digits, captions,
                              wide/tall label parity (PROOF_PLAN.md §5 audit methods a/b/d)

Usage: python3 tests/design_checks.py [--docs docs] [--css docs/assets/styles.css]
                                      [--ledger /root/company/BENCHMARK_01/FACTS_LEDGER.md]
Exit 0 = every check passed.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

FAILURES: list[str] = []
CHECKS = 0
SIGNAL_CSS: str = ""
PROJECT_ORDER: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> bool:
    global CHECKS
    CHECKS += 1
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""))
    if not cond:
        FAILURES.append(label)
    return cond


# --------------------------------------------------------------------------- 1. tokens

TOKEN_LAYER = re.compile(r"@layer\s+tokens\s*\{(.*?)\n\}", re.S)

REQUIRED_TOKENS = [
    "--color-bg-base", "--color-bg-raise", "--color-bg-panel", "--color-ink-1", "--color-ink-2",
    "--color-ink-3", "--color-ink-disabled", "--color-line-rule", "--color-line-strong",
    "--color-accent-signal", "--color-accent-trace", "--color-on-accent", "--color-glass",
    # the warm editorial surface (B2-08: promoted from a print fallback to a first-class
    # screen surface, DESIGN_LANGUAGE.md §4.1 / RECONCILIATION.md)
    "--color-paper", "--color-paper-2", "--color-paper-3", "--color-ink-print",
    "--color-ink-print-2", "--color-ink-print-3", "--color-line-print",
    "--color-line-print-strong", "--color-accent-print", "--color-focus-print",
    "--color-marker-warm",
    "--surface-page", "--surface-raise", "--surface-panel", "--text-body", "--text-secondary",
    "--text-meta", "--text-signal", "--text-link", "--text-trace", "--rule-decor",
    "--rule-boundary", "--fill-action", "--text-on-action", "--ring-outer", "--ring-inner",
    "--signal-size", "--signal-size-print",
    "--font-display", "--font-sans", "--font-mono",
    "--fs-base", "--fs-md", "--fs-lg", "--fs-xl", "--fs-2xl", "--fs-3xl", "--fs-sm",
    "--fs-label", "--fs-micro", "--fs-display-1", "--fs-display-2", "--fs-display-3", "--fs-hero",
    "--lh-display", "--lh-heading", "--lh-body", "--lh-meta", "--ls-display", "--ls-heading",
    "--ls-mono", "--measure", "--wrap", "--page-lead",
    "--space-0", "--space-1", "--space-2", "--space-3", "--space-4", "--space-5", "--space-6",
    "--space-7", "--space-8", "--space-9", "--space-10",
    "--radius-0", "--radius-1", "--radius-2", "--radius-3", "--radius-full",
    "--elev-0", "--elev-1", "--elev-2",
    "--dur-1", "--dur-2", "--dur-3", "--dur-4", "--dur-5",
    "--ease-out-quint", "--ease-out-quart", "--ease-in-quick", "--ease-standard",
    "--z-base", "--z-raise", "--z-nav", "--z-overlay", "--z-skip",
]

DURATION_TOKENS = {"--dur-1": "90ms", "--dur-2": "160ms", "--dur-3": "240ms",
                   "--dur-4": "420ms", "--dur-5": "560ms"}
EASING_TOKENS = {"--ease-out-quint": "cubic-bezier(0.22, 1, 0.36, 1)",
                 "--ease-out-quart": "cubic-bezier(0.25, 1, 0.5, 1)",
                 "--ease-in-quick": "cubic-bezier(0.4, 0, 1, 1)",
                 "--ease-standard": "cubic-bezier(0.2, 0, 0, 1)"}


def token_body(css: str) -> str:
    m = TOKEN_LAYER.search(css)
    return m.group(1) if m else ""


def check_tokens(css: str) -> None:
    print("\n-- 1. token conformance (DESIGN_SYSTEM.md §1/§8.2) --")
    body = token_body(css)
    check(bool(body), "@layer tokens block exists in the shipped stylesheet")
    missing = [t for t in REQUIRED_TOKENS if f"{t}:" not in body]
    check(not missing, "every token the design specifies is declared in @layer tokens",
          f"missing={missing[:8]}" if missing else f"{len(REQUIRED_TOKENS)} tokens present")
    wrong = []
    for key, expected in {**DURATION_TOKENS, **EASING_TOKENS}.items():
        m = re.search(re.escape(key) + r":\s*([^;]+);", body)
        if m and m.group(1).strip() != expected:
            wrong.append(f"{key}={m.group(1).strip()} (documented: {expected})")
    check(not wrong, "the motion tokens hold exactly the documented values",
          "; ".join(wrong) if wrong else "5 durations + 4 easings match ART_DIRECTION.md §7.1")

    rest = css[TOKEN_LAYER.search(css).end():] if TOKEN_LAYER.search(css) else css
    head = css[:TOKEN_LAYER.search(css).start()] if TOKEN_LAYER.search(css) else ""
    offenders = []
    for chunk, offset in ((head, 0), (rest, css[:TOKEN_LAYER.search(css).start()].count("\n")
                                      + css[TOKEN_LAYER.search(css).start():
                                            TOKEN_LAYER.search(css).end()].count("\n"))):
        for i, line in enumerate(chunk.splitlines()):
            stripped = line.strip()
            if re.search(r"#[0-9a-fA-F]{3,8}\b", stripped):
                offenders.append(f"hex colour: {stripped[:70]}")
            if re.search(r"font-size:\s*[\d.]+px", stripped):
                offenders.append(f"px font-size: {stripped[:70]}")
            if re.search(r"(?<![\w-])[\d.]+ms(?![)\w-])", stripped):
                offenders.append(f"ms literal: {stripped[:70]}")
            if "cubic-bezier(" in stripped:
                offenders.append(f"cubic-bezier literal: {stripped[:70]}")
    check(not offenders, "no raw hex / px font-size / ms / cubic-bezier outside @layer tokens",
          f"{len(offenders)} offender(s): {offenders[:4]}" if offenders else
          "components consume semantic tokens only")

    layers = re.search(r"^@layer\s+([^;{}]+);", css, re.M)
    order = [s.strip() for s in layers.group(1).split(",")] if layers else []
    check(order[:6] == ["reset", "tokens", "base", "layout", "components", "states"],
          "the layer order is declared once, states after components",
          " > ".join(order))

    # Elevation is a closed set: outside @layer tokens a box-shadow may only be the elevation
    # token, a zero-offset ring, or the row-rule thickener — so no component can paint a tight,
    # hard, offset drop shadow anywhere on the site (Q11). This is the exhaustive half of the
    # DOM sample in tests/browser_checks.mjs.
    permitted = [
        re.compile(r"^none$"),
        re.compile(r"var\(--elev-\d\)"),
        re.compile(r"^0 0 0 [\d.]+(px|rem)\b"),
        re.compile(r"^0 1px 0 0 var\(--rule-boundary\)$"),
    ]
    shadows = [s.strip() for s in re.findall(r"box-shadow\s*:\s*([^;}]+)", rest)]
    bad = [s for s in shadows if not any(p.search(s) for p in permitted)]
    check(not bad, "every box-shadow outside the token layer is an elevation token or a ring",
          f"unpermitted={bad[:3]}" if bad else
          f"{len(shadows)} shadow declarations, all from the closed elevation set")


# --------------------------------------------------------------------------- 2/3. states & bans

REQUIRED_STATE_SNIPPETS = [
    ("hover", r"\:hover"),
    ("focus-visible", r"\:focus-visible"),
    ("active", r"\:active"),
    ("aria-current", r"aria-current"),
    ("empty state", r"\.empty"),
    ("404 state", r"\.notfound"),
    ("print state", r"@media print"),
    ("selection", r"::selection"),
    ("reduced motion", r"prefers-reduced-motion:\s*reduce"),
    ("no-motion preference", r"prefers-reduced-motion:\s*no-preference"),
    ("no-JS path", r"html\.no-js|\.no-js"),
    ("disabled recipe", r"aria-disabled"),
    ("two-layer focus ring", r"--ring-inner"),
]
BANNED_SNIPPETS = [
    ("transition: all", r"transition\s*:\s*all"),
    ("bare `ease` timing", r"transition[^;}]*\b\d+m?s\s+ease\b"),
    ("ease-in-out", r"ease-in-out"),
    ("linear entrance", r"transition[^;}]*\blinear\b"),
    ("outline: none", r"outline\s*:\s*none"),
    ("transition: none on a state", r"\:hover[^{]*\{[^}]*transition\s*:\s*none"),
]


def check_states(css: str) -> None:
    print("\n-- 2. required states (DESIGN_SYSTEM.md §7) --")
    missing = [name for name, pat in REQUIRED_STATE_SNIPPETS if not re.search(pat, css)]
    check(not missing, "every designed state exists in the shipped stylesheet",
          f"missing={missing}" if missing else f"{len(REQUIRED_STATE_SNIPPETS)} states present")

    print("\n-- 3. banned defaults / banned easings (Q11, ART_DIRECTION.md §7.1) --")
    hits = [name for name, pat in BANNED_SNIPPETS if re.search(pat, css)]
    check(not hits, "no banned transition/easing/reset pattern in the stylesheet",
          f"hits={hits}" if hits else f"{len(BANNED_SNIPPETS)} patterns checked, 0 hits")


# --------------------------------------------------------------------------- 4. motion

RAW_LINES: list[str] = []
DEVIATION_MARKER = "@deviation:"


def _documented_deviation(idx: int, window: int = 6) -> bool:
    return any(DEVIATION_MARKER in RAW_LINES[j]
               for j in range(max(0, idx - window), min(idx + 1, len(RAW_LINES))))


def check_motion(css: str) -> None:
    print("\n-- 4. motion-spec conformance (ART_DIRECTION.md §7) --")
    decls = re.findall(r"transition(?:-duration|-timing-function)?\s*:\s*([^;}]+)", css)
    literal_dur = [d.strip() for d in decls
                   if re.search(r"(?<![\w-])[\d.]+(m?s)\b", d.strip())
                   and "var(" not in d
                   and not re.fullmatch(r"0(m?s)(\s*!important)?", d.strip())]
    check(not literal_dur, "every transition duration is a token (or the 0s reduced-motion stop)",
          f"literals={literal_dur[:3]}" if literal_dur else f"{len(decls)} declarations checked")
    literal_ease = [d.strip() for d in decls
                    if ("ease" in d or "cubic-bezier(" in d) and "var(" not in d]
    check(not literal_ease, "every transition timing function is a token, not a literal",
          f"literals={literal_ease[:3]}" if literal_ease else "0 literal easings")

    banned_prop = re.compile(r"\b(width|height|top|left|margin|padding|all)\b")
    offenders, excused = [], []
    for idx, line in enumerate(css.splitlines()):
        m = re.search(r"transition-property\s*:\s*([^;}]+)", line)
        if not m:
            continue
        if not banned_prop.search(m.group(1)):
            continue
        if _documented_deviation(idx):
            excused.append(m.group(1).strip())
        else:
            offenders.append(m.group(1).strip())
    check(not offenders, "no transition animates width/height/top/left/margin/padding/all",
          f"offenders={offenders}" if offenders else
          f"{excused} documented deviation(s) only" if excused else "0 layout-animating transitions")
    deviations = sorted({ln.split(DEVIATION_MARKER, 1)[1].split()[0].strip()
                         for ln in RAW_LINES if DEVIATION_MARKER in ln})
    check(len(deviations) == 1 and deviations[0] == "motion-padding",
          "exactly one motion deviation exists, and it is the one recorded as a defect",
          f"markers={deviations}")

    used = set(re.findall(r"var\((--dur-\d)\)", css))
    check(used and used.issubset(set(DURATION_TOKENS)),
          "the durations in use are a subset of the documented five",
          f"used={sorted(used)}")
    check("prefers-reduced-motion: reduce" in css and "animation-name: none !important" in css,
          "the reduced-motion path removes every transition and animation without removing state")


# --------------------------------------------------------------------------- 5. contrast

def _srgb(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _srgb(r) + 0.7152 * _srgb(g) + 0.0722 * _srgb(b)


def ratio(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def composite(fg: str, bg: str, alpha: float) -> str:
    f = [int(fg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(bg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    out = [round(f[i] * alpha + b[i] * (1 - alpha)) for i in range(3)]
    return "#" + "".join(f"{v:02x}" for v in out)


# B2-08: the palette is two SURFACES, not one theme, so every pair is graded against the
# surface it actually sits on (DESIGN_LANGUAGE.md §5.2). A pair is only meaningful if the two
# values can be adjacent: the signal token is never graded across surfaces, because the values
# are roles and are deliberately not interchangeable (that cross-surface pair is the recorded
# deliberate-FAIL control, printed at the end of this section).
SURFACE_PALETTE = {
    "warm": {
        "surfaces": ["--color-paper", "--color-paper-2", "--color-paper-3"],
        "inks": [("body", "--color-ink-print"), ("secondary", "--color-ink-print-2"),
                 ("meta", "--color-ink-print-3"), ("signal", "--color-accent-print"),
                 ("marker", "--color-marker-warm")],
        "non_text": [("boundary", "--color-line-print-strong", 3.0),
                     ("focus ring", "--color-focus-print", 3.0),
                     ("signal disc", "--color-accent-print", 3.0)],
        "action": ("--color-ink-print", "--color-paper"),
    },
    "deep": {
        "surfaces": ["--color-bg-base", "--color-bg-raise", "--color-bg-panel"],
        "inks": [("body", "--color-ink-1"), ("secondary", "--color-ink-2"),
                 ("meta", "--color-ink-3"), ("signal", "--color-accent-signal"),
                 ("marker", "--color-accent-trace")],
        "non_text": [("boundary", "--color-line-strong", 3.0),
                     ("focus ring", "--color-ink-1", 3.0),
                     ("signal disc", "--color-accent-signal", 3.0)],
        "action": ("--color-ink-1", "--color-bg-base"),
    },
}


def check_contrast(css: str) -> None:
    print("\n-- 5. palette contrast, computed per pair from the shipped tokens, per SURFACE --")
    tokens = dict(re.findall(r"(--color-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", css))
    check(len(tokens) >= 20, "the shipped stylesheet declares the palette primitives",
          f"{len(tokens)} colour tokens parsed")
    print(f"        tokens: {len(tokens)}")
    fails: list[str] = []
    pairs = 0
    for surface, spec in SURFACE_PALETTE.items():
        print(f"        --- {surface} surface ---")
        print(f"        {'pair':38} {'ratio':>7}  threshold")
        for bg in spec["surfaces"]:
            for name, ink in spec["inks"]:
                thr = 4.5
                fg_v, bg_v = tokens.get(ink), tokens.get(bg)
                if not fg_v or not bg_v:
                    fails.append(f"{surface}/{name} on {bg}: token missing")
                    continue
                r = ratio(fg_v, bg_v)
                ok = r >= thr
                pairs += 1
                print(f"        {name + ' on ' + bg:38} {r:7.2f}  >= {thr}  "
                      f"{'PASS' if ok else 'FAIL'}")
                if not ok:
                    fails.append(f"{surface}: {name} on {bg} = {r:.2f} < {thr}")
        for name, tok, thr in spec["non_text"]:
            for bg in spec["surfaces"]:
                fg_v, bg_v = tokens.get(tok), tokens.get(bg)
                if not fg_v or not bg_v:
                    fails.append(f"{surface}/{name} on {bg}: token missing")
                    continue
                r = ratio(fg_v, bg_v)
                ok = r >= thr
                pairs += 1
                print(f"        {name + ' on ' + bg:38} {r:7.2f}  >= {thr}  "
                      f"{'PASS' if ok else 'FAIL'}")
                if not ok:
                    fails.append(f"{surface}: {name} on {bg} = {r:.2f} < {thr}")
        fg, bg = spec["action"]
        r = ratio(tokens[fg], tokens[bg])
        pairs += 1
        print(f"        {'action fill on its label':38} {r:7.2f}  >= 4.5  "
              f"{'PASS' if r >= 4.5 else 'FAIL'}")
        if r < 4.5:
            fails.append(f"{surface}: action fill = {r:.2f} < 4.5")
    check(not fails, "every text pair >= 4.5:1 and every non-text pair >= 3:1, per surface",
          f"failures={fails}" if fails else f"{pairs} pairs computed, 0 failures")

    # The structural fix for the owner's named failure mode: the SIGNAL hue may never be the
    # action or link colour (DESIGN_LANGUAGE.md §5.2 rule 2). Asserted by reading the shipped
    # declarations, not by trusting the comment.
    body = token_body(css)
    action_offenders = []
    for surface in SURFACE_PALETTE:
        block = re.search(r'\[data-surface="' + surface + r'"\]\s*\{(.*?)\}', body, re.S)
        if not block:
            action_offenders.append(f"{surface}: no token block")
            continue
        for tok in ("--text-link", "--fill-action"):
            m = re.search(re.escape(tok) + r":\s*([^;]+);", block.group(1))
            if m and ("accent-signal" in m.group(1) or "accent-print" in m.group(1)):
                action_offenders.append(f"{surface}: {tok} = {m.group(1).strip()}")
    check(not action_offenders,
          "the signal hue is never the action or link colour on either surface",
          "; ".join(action_offenders) if action_offenders else
          "action is carried by ink, weight and underline (DNA 5.2 rule 3)")

    # The recorded deliberate-FAIL control: the instrument signal value on the warm surface.
    # It must fail, or the "one role, per-surface values" claim is not real.
    cross = ratio(tokens["--color-accent-signal"], tokens["--color-paper"])
    check(cross < 3.0,
          "control: the instrument signal value on the warm surface FAILS (values are per-surface)",
          f"instrument signal on paper = {cross:.2f}:1 (deliberate FAIL control, DNA 5.2 rule 4)")

    # the deep light field lightens the background, so it is measured as a composite
    base = tokens.get("--color-bg-base", "#0c0e13")
    trace = tokens.get("--color-accent-trace", "#58c9be")
    signal = tokens.get("--color-accent-signal", "#f2a93b")
    worst = None
    for alpha in (0.04, 0.06, 0.08):
        for glow in (trace, signal):
            comp = composite(glow, base, alpha)
            for ink in ("--color-ink-1", "--color-ink-2", "--color-ink-3"):
                r = ratio(tokens[ink], comp)
                if worst is None or r < worst[0]:
                    worst = (r, alpha, glow, ink)
    check(worst and worst[0] >= 4.5,
          "the deep-surface light field composite keeps every ink pair >= 4.5:1 at alpha <= 0.08",
          f"worst case {worst[0]:.2f}:1 at alpha {worst[1]} ({worst[2]} / {worst[3]})")


# --------------------------------------------------------------------------- 6. artefacts

STRUCTURAL_WORDS = {
    # connective/enumerative words, the structural section labels PRD.md §3.3 fixes, and the
    # receptacle/annotation names PROOF_PLAN.md §4 specifies. They assert nothing about the
    # person, the work or a quantity.
    "and", "then", "to", "end", "only", "structure", "annotations", "scope", "request",
    "proposed", "action", "pack", "tool", "slot", "server", "documented", "simulated",
    "customer", "conversation", "surface", "operations", "release", "path", "live", "tunnel",
    "e2e", "agent", "lane", "trace", "replayable", "traces", "outcome", "stats", "applied",
}

MEASUREMENT_VOCAB = [r"[\d.]+%", r"\b\d+\s*ms\b", r"\b\d+x\b", r"\bper\s+(second|hour|job|day)\b",
                     r"\brate\b", r"\bcount\b", r"\bavg\b", r"\btotal\b", r"\buptime\b",
                     r"\baccuracy\b", r"\bprecision\b", r"\brecall\b", r"\bf1\b", r"\blatency\b",
                     r"\bthroughput\b", r"\busers\b", r"\bclients\b", r"[$€£]"]

# proper nouns that contain a digit but name a technique, not an amount (PROOF_PLAN.md §5 rule 4)
PERMITTED_DIGIT_WORDS = {"bm25", "e2e"}

WORD_RE = re.compile(r"[a-z0-9][a-z0-9&+.\-]*")


def words_of(text: str) -> list[str]:
    return [w.strip(".-") for w in WORD_RE.findall(text.lower()) if w.strip(".-")]


def svg_labels(svg: str) -> list[str]:
    texts = re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S)
    return [re.sub(r"\s+", " ", html.unescape(t)).strip() for t in texts if t.strip()]


def svg_words(svg: str) -> list[str]:
    """Every word of every label, as a multiset: line breaks differ per layout, words do not."""
    words: list[str] = []
    for label in svg_labels(svg):
        words.extend(words_of(label))
    return sorted(words)


def svg_blocks(html_: str) -> list[str]:
    return re.findall(r"<svg\b.*?</svg>", html_, re.S)


def check_artefacts(docs: Path, ledger: str) -> None:
    print("\n-- 6. artefact audits (PROOF_PLAN.md §5 audit methods a/b/d) --")
    allowed = set(words_of(ledger)) | STRUCTURAL_WORDS
    pages = sorted(docs.rglob("*.html"))
    figures = 0
    uncaptioned: list[str] = []
    unapproved: list[str] = []
    measure_hits: list[str] = []
    digit_hits: list[str] = []
    parity_fails: list[str] = []
    all_labels: set[str] = set()

    def audit(page_name: str, fig: str, kind: str) -> None:
        svgs = svg_blocks(fig)
        if len(svgs) == 2 and svg_words(svgs[0]) != svg_words(svgs[1]):
            only_wide = sorted(set(svg_words(svgs[0])) - set(svg_words(svgs[1])))
            only_tall = sorted(set(svg_words(svgs[1])) - set(svg_words(svgs[0])))
            parity_fails.append(f"{page_name} ({kind}): wide-only={only_wide[:4]} "
                                f"tall-only={only_tall[:4]}")
        for svg in svgs:
            for label in svg_labels(svg):
                all_labels.add(label)
                low = label.lower()
                for word in words_of(low):
                    if word not in allowed:
                        unapproved.append(f"{page_name}: {word!r} in {label!r}")
                    if re.search(r"\d", word) and word not in PERMITTED_DIGIT_WORDS:
                        digit_hits.append(f"{page_name}: {word!r} in {label!r}")
                for pat in MEASUREMENT_VOCAB:
                    if re.search(pat, low):
                        measure_hits.append(f"{page_name}: {label!r} ~ {pat}")

    for page in pages:
        html_ = page.read_text(encoding="utf-8")
        for fig in re.findall(r"<figure class=\"artefact\".*?</figure>", html_, re.S):
            figures += 1
            if "<figcaption>" not in fig or "Schematic" not in fig:
                uncaptioned.append(page.name)
            audit(page.name, fig, "artefact")
        for fig in re.findall(r"<figure class=\"system-map\".*?</figure>", html_, re.S):
            figures += 1
            if "Schematic" not in fig:
                uncaptioned.append(f"{page.name} (system map)")
            audit(f"{page.name} (system map)", fig, "system map")

    check(figures == 13,
          "13 artefacts render (hero system map + SmartOps band + 10 project pages + 404 map)",
          f"found {figures}")
    check(not uncaptioned, "every artefact carries the mandatory scope caption",
          f"uncaptioned={uncaptioned[:3]}" if uncaptioned else "13/13 captioned")
    check(not unapproved,
          "label diff: every word of every diagram label is a ledger word or structural",
          f"{len(unapproved)} unapproved: {unapproved[:6]}" if unapproved else
          f"{len(all_labels)} distinct labels, every word traced to the ledger")
    check(not measure_hits, "measurement-vocabulary scan of every diagram label: 0 hits",
          f"hits={measure_hits[:4]}" if measure_hits else
          f"{len(MEASUREMENT_VOCAB)} patterns checked against {len(all_labels)} labels")
    check(not digit_hits, "digits in diagram labels: only the permitted proper nouns (BM25, E2E)",
          f"hits={digit_hits[:4]}" if digit_hits else "0 quantity-bearing labels")
    check(not parity_fails, "wide and vertical-rail variants carry identical label words",
          f"{parity_fails[:3]}" if parity_fails else "13/13 artefacts label-identical")
    print(f"        distinct diagram labels: {len(all_labels)}")


# --------------------------------------------------------------------------- 7. the motif's switch

def check_provenance_switch() -> None:
    """The attribution rule's documented fallback (DESIGN_SYSTEM.md §6.10) must be real."""
    print("\n-- 7. attribution-rule switch integrity (tier | plain | off) --")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import copy
    import build_site as B  # noqa: PLC0415

    cfg = B.load_config(B.DEFAULT_CONFIG)
    if cfg["provenance"]["tags"] != "tier":
        check(False, "the delivered build ships provenance.tags='tier'",
              f"delivered value is {cfg['provenance']['tags']!r}")
        return
    check(True, "the delivered build ships provenance.tags='tier'",
          "the identity motif is on in the shipped state")

    def sig(text: str) -> str:
        return "\n".join(line for line in text.splitlines() if line.strip())

    tier = B.render_all(copy.deepcopy(cfg), None)
    check("<abbr>S" in tier["index.html"] and "srctag" in tier["index.html"],
          "tags=tier: the source tier is seated on the hairline")

    cfg_plain = copy.deepcopy(cfg)
    cfg_plain["provenance"]["tags"] = "plain"
    plain = B.render_all(cfg_plain, None)
    check("SOURCED" in plain["index.html"] and "<abbr>" not in plain["index.html"],
          "tags=plain: one step down to a plain SOURCED mark, no other design change",
          "index carries the plain mark" if "SOURCED" in plain["index.html"] else "mark missing")
    check(sig(re.sub(r'<p class="attr-rule".*?</p>', "", plain["index.html"]))
          == sig(re.sub(r'<p class="attr-rule".*?</p>', "", tier["index.html"])),
          "tags=plain changes only the attribution rule itself, nothing around it")
    check(sig(plain["index.html"]) != sig(tier["index.html"]),
          "tags=plain is a real change (the two builds differ where the tag is rendered)")

    cfg_off = copy.deepcopy(cfg)
    cfg_off["provenance"]["tags"] = "off"
    off = B.render_all(cfg_off, None)
    check("NOT YET PUBLISHED" in off["index.html"] and "<abbr>" not in off["index.html"],
          "tags=off: the evidence band renders the designed empty state, never a blank area",
          "empty block present" if "NOT YET PUBLISHED" in off["index.html"] else "missing")
    check("Project page" not in off["index.html"] and "srctag" not in off["index.html"],
          "tags=off: no stray attribution mark survives on the index")
    check("NOT YET PUBLISHED" not in tier["index.html"],
          "tags=tier: the designed empty state is not rendered when the motif is on")
    print("        the motif's fallback costs one config line and one build, as specified")


# --------------------------------------------------------------------------- 8. the signal

# B2-08 check (a): signal scarcity. The mark is countable, so scarcity is asserted mechanically
# rather than left to taste (DESIGN_LANGUAGE.md §3.4, §3.7). Budget per artifact by mode; hard
# ceiling 3; at most one per plane; every mark attributable to C1-C4 with a label beside it.
MODE_SIGNAL_BUDGET = {"M1": 1, "M2": 2, "M3": 1, "M4": 1}
SIGNAL_CEILING = 3

SIGNAL_EL = re.compile(r'<span class="signal"([^>]*)>(.*?)</span>', re.S)
ADMISSION = re.compile(r'data-admission="(C[1-4])"')
PLANE_OPEN = re.compile(r'<section class="plane([^>]*)>')


def parse_page(html_: str) -> dict:
    body = re.search(r"<body([^>]*)>", html_)
    attrs = body.group(1) if body else ""
    def attr(name: str, default: str = "") -> str:
        m = re.search(name + r'="([^"]*)"', attrs)
        return m.group(1) if m else default
    planes = []
    matches = list(PLANE_OPEN.finditer(html_))
    for i, m in enumerate(matches):
        attrs_s = m.group(1)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(html_)
        chunk = html_[m.end():end]
        surface = re.search(r'data-surface="([^"]+)"', attrs_s)
        label = re.search(r'data-plane="([^"]+)"', attrs_s)
        planes.append({
            "surface": surface.group(1) if surface else None,
            "label": label.group(1) if label else "unnamed",
            "signals": len(SIGNAL_EL.findall(chunk)),
        })
    signals = []
    for attrs_s, label in SIGNAL_EL.findall(html_):
        adm = ADMISSION.search(attrs_s)
        signals.append({"admission": adm.group(1) if adm else None,
                        "label": re.sub(r"<[^>]+>", "", label).strip()})
    return {"page": attr("data-page"), "mode": attr("data-mode"), "arch": attr("data-arch"),
            "surface": attr("data-surface"), "planes": planes, "signals": signals}


def check_signal_scarcity(docs: Path) -> None:
    print("\n-- 8. signal scarcity (DESIGN_LANGUAGE.md 3.4 / 3.7) --")
    print("        proxy: every <span class=\"signal\"> in the built HTML, counted per page and")
    print("        per plane, with its admission condition read from data-admission.")
    pages = sorted(docs.rglob("*.html"))
    rows = []
    problems: list[str] = []
    unattributed: list[str] = []
    unlabelled: list[str] = []
    plural: list[str] = []
    for page in pages:
        html_ = page.read_text(encoding="utf-8")
        info = parse_page(html_)
        rel = str(page.relative_to(docs))
        total = len(info["signals"])
        budget = MODE_SIGNAL_BUDGET.get(info["mode"], 0)
        rows.append((rel, info["mode"], info["arch"], total, budget))
        if total > budget:
            problems.append(f"{rel}: {total} signals > mode {info['mode']} budget {budget}")
        if total > SIGNAL_CEILING:
            problems.append(f"{rel}: {total} signals > the hard ceiling {SIGNAL_CEILING}")
        for pl in info["planes"]:
            if pl["signals"] > 1:
                problems.append(f"{rel}: plane '{pl['label']}' carries {pl['signals']} signals")
        for s in info["signals"]:
            if not s["admission"]:
                unattributed.append(f"{rel}: {s['label']!r} names no C1-C4 condition")
            if not s["label"]:
                unlabelled.append(f"{rel}: a signal carries no label")
        if re.search(r"<li[^>]*>\s*<span class=\"signal\"", html_):
            plural.append(f"{rel}: a signal is used as a list bullet")
        if re.search(r"<t[dh][^>]*>\s*<span class=\"signal\"", html_):
            plural.append(f"{rel}: a signal sits in a table cell (a plurality)")

    print(f"        {'page':34} {'mode':5} {'arch':5} {'signals':>7}  budget")
    for rel, mode, arch, total, budget in rows:
        print(f"        {rel:34} {mode:5} {arch:5} {total:>7}  {budget}")
    zero = sum(1 for r in rows if r[3] == 0)
    check(not problems, "no page exceeds its mode's signal budget or the hard ceiling",
          "; ".join(problems[:4]) if problems else
          f"{len(rows)} pages, {zero} of them with ZERO signals (the language's normal state)")
    check(not unattributed, "every signal names its admission condition (C1-C4)",
          "; ".join(unattributed[:4]) if unattributed else
          f"{sum(r[3] for r in rows)} marks, all attributable")
    check(not unlabelled, "every signal carries an adjacent label",
          "; ".join(unlabelled[:3]) if unlabelled else "no unlabelled mark exists")
    check(not plural, "no signal is used as a bullet or a per-row plurality",
          "; ".join(plural[:3]) if plural else "the mark is never a column")

    # the label must be set in the instrument voice, next to a mark that is never colour-alone
    css_info = SIGNAL_CSS
    check("font-family: var(--font-mono)" in css_info and "text-transform: uppercase" in css_info,
          "the signal label is set in the instrument voice (mono, labellable)",
          "declared once on .signal")
    check("background-color: var(--text-signal)" in css_info,
          "the mark is drawn from the SIGNAL role, not from an arbitrary value",
          "the disc consumes --text-signal only")


# --------------------------------------------------------------------------- 9. anti-template

# B2-08 check (b): the anti-template rule (DESIGN_LANGUAGE.md §6.3). The proxy is measurable and
# parsed from the built files, never asserted:
#   D1 section order      — the sequence of data-plane values, compared as lists
#   D2 type-scale emphasis— the mode's lead type step / the body step, resolved from the CSS
#   D3 grid archetype     — the declared data-arch plus the number of distinct planes
#   D4 surface dominance  — the leading surface and its share of the artifact's planes
#   D5 motif placement    — the signal count and where the mark sits (leading / inline / absent)
def resolve_css_numbers(css: str) -> dict[str, float]:
    """Resolve the fixed type ramp to px and the per-mode lead step (16px root)."""
    root = re.search(r":root\s*\{(.*?)\n  \}", css, re.S)
    body = root.group(1) if root else ""
    vals: dict[str, float] = {}

    def px(var: str, seen: str = "") -> float | None:
        m = re.search(re.escape(var) + r":\s*([^;]+);", body)
        if not m:
            return None
        v = m.group(1).strip()
        if v.startswith("var("):
            inner = v[4:-1].strip()
            return None if inner == seen else px(inner, var)
        num = re.match(r"([\d.]+)(rem|px)", v)
        if not num:
            return None
        return float(num.group(1)) * (16.0 if num.group(2) == "rem" else 1.0)

    for name in ("--fs-base", "--fs-hero", "--fs-3xl", "--fs-2xl", "--fs-display-1"):
        v = px(name)
        if v:
            vals[name] = v
    for mode in MODE_SIGNAL_BUDGET:
        m = re.search(r'\[data-mode="' + mode + r'"\]\s*\{\s*--page-lead:\s*var\(([^)]+)\)', css)
        if m:
            v = vals.get(m.group(1).strip())
            if v:
                vals[f"lead:{mode}"] = v
    return vals


def check_variability(docs: Path, css: str) -> None:
    print("\n-- 9. anti-template: the variability proxy D1-D5 (DESIGN_LANGUAGE.md 6.3) --")
    vals = resolve_css_numbers(css)
    body_px = vals.get("--fs-base", 17.0)
    order = ["index.html"] + [f"projects/{s}.html" for s in PROJECT_ORDER]
    series = []
    for rel in order:
        p = docs / rel
        if not p.exists():
            continue
        info = parse_page(p.read_text(encoding="utf-8"))
        planes = info["planes"]
        surfaces = [pl["surface"] for pl in planes]
        warm = surfaces.count("warm")
        deep = surfaces.count("deep")
        lead_surface = "warm" if warm >= deep else "deep"
        share = round(100 * max(warm, deep) / max(1, len(planes)))
        lead_px = vals.get(f"lead:{info['mode']}")
        emphasis = round(lead_px / body_px, 2) if lead_px else None
        n = len(info["signals"])
        if n == 0:
            motif = "absent"
        elif planes and planes[0]["signals"]:
            motif = "leading"
        else:
            motif = "inline"
        series.append({
            "page": rel, "mode": info["mode"], "arch": info["arch"],
            "d1": [pl["label"] for pl in planes],
            "d2": emphasis, "d3": (info["arch"], len(planes)),
            "d4": (lead_surface, share), "d5": (n, motif),
        })

    print(f"        {'page':34} {'mode':5} {'arch':5} {'D2':>5}  {'D4 leading':14} {'D5 motif':10} D1")
    for s in series:
        print(f"        {s['page']:34} {s['mode']:5} {s['arch']:5} {str(s['d2']):>5}  "
              f"{s['d4'][0] + ' ' + str(s['d4'][1]) + '%':14} {str(s['d5'][1]):10} "
              f"{'>'.join(s['d1'])}")

    def differs(a: dict, b: dict) -> list[str]:
        d = []
        if a["d1"] != b["d1"]:
            d.append("D1")
        if a["d2"] != b["d2"]:
            d.append("D2")
        if a["d3"] != b["d3"]:
            d.append("D3")
        if a["d4"] != b["d4"]:
            d.append("D4")
        if a["d5"] != b["d5"]:
            d.append("D5")
        return d

    archs = {s["arch"] for s in series}
    check(len(archs) >= 3, "the series uses at least three layout archetypes",
          f"{len(archs)} used: {sorted(archs)}")
    clash = [f"{series[i]['page']} / {series[i + 1]['page']}"
             for i in range(len(series) - 1) if series[i]["arch"] == series[i + 1]["arch"]]
    check(not clash, "no two consecutive pages in the series share an archetype",
          f"clashes={clash}" if clash else f"{len(series) - 1} adjacent pairs checked")

    weak = []
    for i in range(len(series) - 1):
        d = differs(series[i], series[i + 1])
        if len(d) < 2:
            weak.append(f"{series[i]['page']} / {series[i + 1]['page']} differ on {d}")
    check(not weak, "every adjacent pair differs on at least 2 of the 5 dimensions",
          "; ".join(weak[:3]) if weak else
          f"{len(series) - 1} pairs, minimum 2 dimensions, prose not consulted")

    demo = {s["page"]: s for s in series}
    trio = ["index.html", "projects/sama-soc-triage.html", "projects/pulsesec.html"]
    missing = [t for t in trio if t not in demo]
    pairs_bad = []
    for i in range(len(trio)):
        for j in range(i + 1, len(trio)):
            if trio[i] in demo and trio[j] in demo:
                d = differs(demo[trio[i]], demo[trio[j]])
                if len(d) < 2:
                    pairs_bad.append(f"{trio[i]} vs {trio[j]}: {d}")
    check(not missing and not pairs_bad,
          "the three demonstration artefacts (index + two project pages) differ pairwise on >= 2",
          "; ".join(pairs_bad) if pairs_bad else
          "index (M1/A2) vs SAMA (M2/A4) vs PulseSec (M4/A5): all pairs >= 2 of 5")
    modes = {s["mode"] for s in series}
    check(len(modes) >= 2, "the series uses more than one expression mode",
          f"{len(modes)} modes: {sorted(modes)}")


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--css", default="docs/assets/styles.css")
    ap.add_argument("--ledger", default="/root/company/BENCHMARK_01/FACTS_LEDGER.md")
    args = ap.parse_args()

    docs = Path(args.docs).resolve()
    raw_css = Path(args.css).read_text(encoding="utf-8")
    # Comments are blanked (never deleted) so line numbers stay aligned with the raw file:
    # a `@deviation:` marker is read from the raw lines, everything else from the code.
    global RAW_LINES, SIGNAL_CSS, PROJECT_ORDER
    RAW_LINES = raw_css.splitlines()
    css = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), raw_css, flags=re.S)
    SIGNAL_CSS = " ".join(re.findall(r"\.signal(?:::before)?\s*\{[^}]*\}", css))
    ledger = Path(args.ledger).read_text(encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import site_content as _C  # noqa: PLC0415
    PROJECT_ORDER = list(_C.PROJECT_ORDER)

    print("=" * 78)
    print("DESIGN CHECKS — shipped stylesheet + built artefacts")
    print("(B2-02 mechanics, extended in B2-08 for the SIGNAL/MTR design language)")
    print(f"docs   = {docs}")
    print(f"css    = {args.css}")
    print("=" * 78)
    check_tokens(css)
    check_states(css)
    check_motion(css)
    check_contrast(css)
    check_artefacts(docs, ledger)
    check_provenance_switch()
    check_signal_scarcity(docs)
    check_variability(docs, css)

    print("\n" + "=" * 78)
    print(f"checks run: {CHECKS}   failures: {len(FAILURES)}")
    for f in FAILURES:
        print("  FAILED: " + f)
    print("DESIGN CHECKS RESULT: " + ("PASS" if not FAILURES else "FAIL"))
    print("=" * 78)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
