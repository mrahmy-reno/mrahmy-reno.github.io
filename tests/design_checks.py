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
 10. the evidence objects   — object KINDS per VARIANT (B2-05b / N2) and the typed `dg-signal`
                              edges, asserted in the built SVG per page (B2-05b / N3)
 11. craft regressions      — the source half of D1/D2 and of the mid-word break class (N1/N7)
 13. the shipped face       — D6/D6b, including the token name across the kit and the DNA (N6)

Usage: python3 tests/design_checks.py [--docs docs] [--css docs/assets/styles.css]
                                      [--ledger /root/company/BENCHMARK_01/FACTS_LEDGER.md]
                                      [--company /root/company/BENCHMARK_01]
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
    pair_fails: list[str] = []
    parity_fails: list[str] = []
    all_labels: set[str] = set()

    def audit(page_name: str, fig: str, kind: str) -> None:
        svgs = svg_blocks(fig)
        # B2-04 / D1: the pair audit is now structural. Every figure must carry COMPLETE
        # wide/tall pairs (one of each, matched by the aria-labelledby uid), and the two
        # variants of a pair must carry identical label words. The old check only looked at
        # figures that happened to contain exactly two SVGs.
        groups: dict[str | None, list[str]] = {}
        for svg in svgs:
            m = re.search(r'aria-labelledby="([^"]+)"', svg)
            base = None
            if m:
                first = m.group(1).split()[0]
                base = first[:-2] if first.endswith("-t") else first
                if base.endswith("-v"):
                    base = base[:-2]
            groups.setdefault(base, []).append(svg)
        for base, group in groups.items():
            if base is None or len(group) != 2:
                pair_fails.append(f"{page_name} ({kind}): {base} has {len(group)} variant(s)")
                continue
            if svg_words(group[0]) != svg_words(group[1]):
                only_wide = sorted(set(svg_words(group[0])) - set(svg_words(group[1])))
                only_tall = sorted(set(svg_words(group[1])) - set(svg_words(group[0])))
                parity_fails.append(f"{page_name} ({kind}): {base} wide-only={only_wide[:4]} "
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

    check(figures == 17,
          "17 artefacts render (index: run trace + typed-contract excerpt; 10 project pages; the "
          "second interface object on SAMA, SmartOps, Milo and PulseSec; 404 system map)",
          f"found {figures}")
    check(not uncaptioned, "every artefact carries the mandatory scope caption",
          f"uncaptioned={uncaptioned[:3]}" if uncaptioned else "17/17 captioned")
    check(not unapproved,
          "label diff: every word of every diagram label is a ledger word or structural",
          f"{len(unapproved)} unapproved: {unapproved[:6]}" if unapproved else
          f"{len(all_labels)} distinct labels, every word traced to the ledger")
    check(not measure_hits, "measurement-vocabulary scan of every diagram label: 0 hits",
          f"hits={measure_hits[:4]}" if measure_hits else
          f"{len(MEASUREMENT_VOCAB)} patterns checked against {len(all_labels)} labels")
    check(not digit_hits, "digits in diagram labels: only the permitted proper nouns (BM25, E2E)",
          f"hits={digit_hits[:4]}" if digit_hits else "0 quantity-bearing labels")
    check(not pair_fails, "every artefact ships a complete wide + vertical-rail pair",
          f"{pair_fails[:3]}" if pair_fails else "17/17 figures carry matched pairs")
    check(not parity_fails, "wide and vertical-rail variants of every artefact carry identical "
          "label words",
          f"{parity_fails[:3]}" if parity_fails else "17/17 artefacts label-identical")
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
    # B2-04 / D5: "tier" no longer publishes the tier token as visible text. It writes the tier
    # to the DOM (data-source-tiers) and renders a human source sentence instead; the visible
    # form must not contain a tier ID.
    check('data-source-tiers="S' in tier["index.html"] and "srctag" in tier["index.html"],
          "tags=tier: the tier is seated on the hairline as machine-readable data, not as text")
    check(not re.search(r">\s*S[1235]\s*<", tier["index.html"]),
          "tags=tier: no bare tier token is rendered as visible text (D5)")

    cfg_plain = copy.deepcopy(cfg)
    cfg_plain["provenance"]["tags"] = "plain"
    plain = B.render_all(cfg_plain, None)
    check("SOURCED" in plain["index.html"] and "data-source-tiers" not in plain["index.html"],
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
    check("NOT YET PUBLISHED" in off["index.html"] and "data-source-tiers" not in off["index.html"],
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


def _artefact_signature(docs: Path, rel: str) -> tuple:
    """B2-04 / D8, dimension D6: the artefact's own structure, read from the built SVG.

    The proxy's first five dimensions are declared (mode, arch, token ratio, surface share,
    motif) and cannot tell two pages apart when their declarations match. This one is measured
    from the object itself: how many nodes, gates, notes and panels it has, whether it draws a
    bracketed set, a boundary rule or a closing lane. Two pages that differ in what their
    artefact draws are different artefacts.
    """
    page = docs / rel
    if not page.exists():
        return ()
    html_ = page.read_text(encoding="utf-8")
    figs = re.findall(r"<figure class=\"artefact\".*?</figure>", html_, re.S)
    if not figs:
        return ()
    sig = []
    for fig in figs:
        wide = _wide_svg(fig)
        if not wide:
            continue
        sig.append((
            wide.count('class="dg-box"'), wide.count('class="dg-gate"'),
            wide.count('class="dg-note"'), wide.count('class="dg-shape"'),
            wide.count("dg-dashed") > 0,
            len(set(t for _y, t in _svg_texts(wide))),
        ))
    return tuple(sig)


def check_variability(docs: Path, css: str) -> None:
    print("\n-- 9. anti-template: the variability proxy D1-D6 (DESIGN_LANGUAGE.md 6.3) --")
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
            "d6": _artefact_signature(docs, rel),
        })

    print(f"        {'page':34} {'mode':5} {'arch':5} {'D2*':>5}  {'D4 leading':14} "
          f"{'D5 motif':10} D1")
    for s in series:
        print(f"        {s['page']:34} {s['mode']:5} {s['arch']:5} {str(s['d2']):>5}  "
              f"{s['d4'][0] + ' ' + str(s['d4'][1]) + '%':14} {str(s['d5'][1]):10} "
              f"{'>'.join(s['d1'])}")
    print("        D2* = the DECLARED token ratio (the mode's lead step / the body step read "
          "from the stylesheet).")
    print("        The RENDERED emphasis is viewport-dependent (the display steps are clamp()s) "
          "and is measured in")
    print("        tests/browser_checks.mjs against the 3.0 floor. See B2-03 D12.")

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
        if a["d6"] != b["d6"]:
            d.append("D6")
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
    check(not weak, "every adjacent pair differs on at least 2 of the 6 dimensions",
          "; ".join(weak[:3]) if weak else
          f"{len(series) - 1} pairs, minimum 2 dimensions, prose not consulted")

    # B2-04 / D8: the proxy used to compare ADJACENT pages only, so SAMA and Tonsy-GPT passed
    # while being identical on all five measured dimensions. Every pair is now compared, and a
    # sixth dimension measures the artefact itself. Two pages that share an expression profile
    # (same mode AND same archetype) are the risky case the bar's §3.1 step 3 names: they must
    # still be told apart, so they are required to differ on the measured dimension D6.
    identical = []
    profile_twins = []
    n_pairs = 0
    for i in range(len(series)):
        for j in range(i + 1, len(series)):
            n_pairs += 1
            d = differs(series[i], series[j])
            if not d:
                identical.append(f"{series[i]['page']} == {series[j]['page']}")
            same_profile = (series[i]["mode"] == series[j]["mode"]
                            and series[i]["arch"] == series[j]["arch"])
            if same_profile and "D6" not in d:
                profile_twins.append(f"{series[i]['page']} vs {series[j]['page']}: {d}")
    check(not identical,
          "no two pages in the series are identical on all 6 dimensions (all pairs compared)",
          "; ".join(identical[:4]) if identical else f"{n_pairs} pairs compared, 0 identical")
    check(not profile_twins,
          "pages sharing an expression profile (mode + archetype) still differ on the measured "
          "artefact dimension D6",
          "; ".join(profile_twins[:4]) if profile_twins else
          f"every same-profile pair differs in what its artefact draws")

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


# --------------------------------------------------------------------------- 10. the object kinds

# B2-04 / D3 + D7. The critique's central finding was that every artefact was the same object —
# a stack of outlined boxes each holding one label — and that the section built to show work drew
# the ten project names. These checks assert the repair at the level of the objects themselves:
# two object KINDS on the index, a run trace whose cross-cutting controls are drawn above the run
# rather than between two stages, and a contract excerpt that is not a box stack.

def _svg_texts(svg: str) -> list[tuple[float, str]]:
    out = []
    for m in re.finditer(r'<text[^>]*\by="([\d.]+)"[^>]*>(.*?)</text>', svg, re.S):
        out.append((float(m.group(1)), re.sub(r"\s+", " ", html.unescape(m.group(2))).strip()))
    return out


def _wide_svg(fig: str) -> str:
    for svg in svg_blocks(fig):
        if 'class="dg art-wide"' in svg:
            return svg
    return ""


def _variant_of(svg: str) -> str:
    head = svg.split(">", 1)[0]
    if "art-wide" in head:
        return "wide"
    if "art-tall" in head:
        return "tall"
    return "?"


def _model_signals() -> dict[str, tuple[int, bool]]:
    """{artefact <title>: (signalled units, whether the FIRST unit is signalled)} (B2-05b / N3).

    Keyed by the artefact's own SVG `<title>`, so the audit resolves the diagram a page actually
    publishes back to the model that drew it, instead of assuming which page draws which object.
    """
    out: dict[str, tuple[int, bool]] = {}
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
    import artefacts as _A  # noqa: PLC0415

    for meta in _A.ARTEFACT_META.values():
        units = list(meta.get("units") or meta.get("stages") or [])
        out[meta["title"]] = (sum(1 for u in units if u.get("signal")),
                              bool(units and units[0].get("signal")))
    return out


def check_evidence_objects(docs: Path) -> None:
    print("\n-- 10. the evidence objects (B2-04 / D3, D7) --")
    index = (docs / "index.html").read_text(encoding="utf-8")
    figs = re.findall(r"<figure class=\"artefact\".*?</figure>", index, re.S)
    check(len(figs) == 2,
          "the index's Work, shown plane draws two objects (a run trace and a contract excerpt)",
          f"{len(figs)} artefact figure(s)")
    if len(figs) != 2:
        return

    trace, contract = figs
    stages = ["context construction", "active investigation", "threat modeling", "quality guards",
              "verdict generation"]
    lines = _svg_texts(_wide_svg(trace))
    words = [w for _y, t in lines for w in t.split()]
    positions = []
    for stage in stages:
        first = stage.split()[0]
        positions.append(words.index(first) if first in words else -1)
    check(-1 not in positions and positions == sorted(positions),
          "D7: the run trace carries the ledger's five workflow components, in the ledger's order",
          f"positions={positions}" if -1 in positions or positions != sorted(positions)
          else f"5/5 in order: {', '.join(stages)}")

    def top(label_first_word: str) -> float | None:
        ys = [y for y, t in lines if label_first_word in t.split()]
        return min(ys) if ys else None

    cross = ["typed", "grounding/evidence"]
    first_stage_y, cross_ys = top("context"), [top(w) for w in cross]
    above = (first_stage_y is not None and all(y is not None and y < first_stage_y
                                               for y in cross_ys))
    check(above,
          "D7: typed contracts and grounding/evidence controls are drawn as cross-cutting "
          "annotations above the whole run, not as gates between two stages",
          f"controls at y={cross_ys}, first stage at y={first_stage_y}")
    between = []
    stage_ys = sorted(y for y in (top(s.split()[0]) for s in stages) if y is not None)
    for word, y in zip(cross, cross_ys):
        if y is not None and any(a < y < b for a, b in zip(stage_ys, stage_ys[1:])):
            between.append(word)
    check(not between, "D7: no control label sits between two stages of the run",
          f"between stages: {between}" if between else "0 labels interleaved")

    # B2-05b / N2 — the assertion is per VARIANT, not per figure. The old form called `_wide_svg`
    # explicitly, so it was variant-blind by construction: it passed while the tall variant — the
    # one a phone visitor gets — redrew the code surface as the retired chain of five `dg-box`
    # rectangles. Every variant that can be displayed must be the same kind of object.
    variants = svg_blocks(contract)
    bad_variants = []
    for svg in variants:
        rows_ = [t for _y, t in _svg_texts(svg)]
        shapes_ = svg.count('class="dg-shape"')
        boxes_ = svg.count('class="dg-box"')
        if not (shapes_ >= 1 and boxes_ == 0 and len(rows_) >= 5):
            bad_variants.append(f"{_variant_of(svg)}: dg-shape={shapes_} dg-box={boxes_} "
                                f"text rows={len(rows_)}")
    check(len(variants) == 2 and not bad_variants,
          "D3: EVERY variant of the contract excerpt is a code surface (header + field rows in "
          "one panel), not a chain of outlined boxes",
          "; ".join(bad_variants) if bad_variants else
          f"{len(variants)} variants, each dg-shape>=1 dg-box=0 with >=5 field lines")
    non_distinct = []
    for svg in variants:
        rows_ = [t for _y, t in _svg_texts(svg)]
        if len(set(rows_)) != len(rows_):
            non_distinct.append(f"{_variant_of(svg)}: {len(set(rows_))}/{len(rows_)} distinct")
    check(not non_distinct,
          "D3: every row of the contract excerpt is a distinct field line, in both variants",
          "; ".join(non_distinct) if non_distinct else
          f"{len(variants)} variants, all rows distinct")

    sama = (docs / "projects" / "sama-soc-triage.html").read_text(encoding="utf-8")
    check(len(re.findall(r"<figure class=\"artefact\".*?</figure>", sama, re.S)) == 2,
          "D3: the flagship page (SAMA) carries both objects — a run trace and a contract excerpt")

    # ---------------------------------------------------------------- B2-09 / D3: per flagship
    # B2-05's §F.4 finding: the code-surface object existed on the index and SAMA only; the other
    # three flagship pages carried a single schematic, so "at least one object per flagship page
    # that could only exist if the system were real" was not met. This asserts it page by page,
    # in every displayed variant: a figure counts as an interface object only when EVERY variant
    # is a code surface (dg-shape >= 1, dg-box == 0) with distinct field lines.
    FLAGSHIPS = ["sama-soc-triage", "smartops-soc-app", "milo-ai-employee", "pulsesec"]
    interface_missing: list[str] = []
    for slug in FLAGSHIPS:
        page_html = (docs / "projects" / f"{slug}.html").read_text(encoding="utf-8")
        figs_ = re.findall(r"<figure class=\"artefact\".*?</figure>", page_html, re.S)
        ok = False
        for fig in figs_:
            variants_ = svg_blocks(fig)
            if not variants_:
                continue
            good = True
            for svg in variants_:
                rows_ = [t for _y, t in _svg_texts(svg)]
                if not (svg.count('class="dg-shape"') >= 1 and svg.count('class="dg-box"') == 0
                        and len(rows_) >= 5 and len(set(rows_)) == len(rows_)):
                    good = False
                    break
            if good:
                ok = True
                break
        if not ok:
            interface_missing.append(slug)
    check(not interface_missing,
          "D3: every flagship page carries an interface object that could only exist if the "
          "system were real — a code surface (dg-shape panel + field rows, dg-box = 0) in every "
          "variant, not a chain of outlined boxes",
          f"missing on: {interface_missing}" if interface_missing else
          f"{len(FLAGSHIPS)}/4 flagship pages carry one "
          f"(SAMA, SmartOps, Milo, PulseSec — plus the index)")

    # ------------------------------------------------------------------ B2-05b / N3: typed edges
    # The claim "the run trace is drawn with typed edges (signal edges where the ledger's own
    # emphasis mark sits)" was true of the MODEL and false of the SHIPPED TREE: `dg-signal`
    # counted 0 everywhere, because `tools/artefacts.py` classed the edge *after* stage i from
    # `stage[i].signal` while every signalled stage is the last one (`i < n - 1` false) — dead
    # code. These four assertions make the typing non-optional: it must resolve, it must render,
    # and it must render on every page whose model asks for it.
    signals = _model_signals()
    first_signalled = [t for t, (_n, first) in signals.items() if first]
    check(not first_signalled,
          "N3: no artefact model marks its FIRST unit as the signal — the typing is the edge that "
          "arrives at a unit (a first unit has no arriving edge to type)",
          f"first-unit signal on: {first_signalled}" if first_signalled else
          f"{len(signals)} artefact models audited, 0 with a first-unit signal")
    unresolved, short, total_signals = [], [], 0
    for page in sorted(docs.rglob("*.html")):
        svgs = svg_blocks(page.read_text(encoding="utf-8"))
        if not svgs:
            continue
        titles = set()
        for svg in svgs:
            m = re.search(r"<title[^>]*>(.*?)</title>", svg, re.S)
            if m:
                titles.add(re.sub(r"\s+", " ", html.unescape(m.group(1))).strip())
        want = 0
        for title in sorted(titles):
            if title in signals:
                want += signals[title][0]
            else:
                unresolved.append(f"{page.name}: {title[:48]}")
        got = sum(svg.count("dg-signal") for svg in svgs)
        total_signals += got
        if want and got < want:
            short.append(f"{page.name}: {got} dg-signal for {want} signalled unit(s)")
    check(not unresolved,
          "N3: every published diagram resolves to an artefact model by its own title, so the "
          "signal audit cannot quietly skip a page",
          f"unresolved titles: {unresolved[:4]}" if unresolved else
          f"every <title> in the built tree matched a model ({len(signals)} models)")
    check(not short,
          "N3: every signalled unit renders a typed (dg-signal) edge in the built SVG",
          "; ".join(short) if short else
          "every page whose model sets signal: true carries >= 1 dg-signal per signalled unit")
    check(total_signals >= sum(n for n, _f in signals.values()),
          "N3: the tree-wide count of dg-signal elements is >= the number of signalled units",
          f"{total_signals} dg-signal elements rendered for "
          f"{sum(n for n, _f in signals.values())} signalled units")


# --------------------------------------------------------------------------- 11. craft regressions

def _css_rules(css: str) -> list[tuple[str, str, str]]:
    """(selector, declarations, ancestor at-rules) for every rule, in source order."""
    rules: list[tuple[str, str, str]] = []
    stack: list[str] = []
    buf = ""
    for ch in css:
        if ch == "{":
            stack.append(buf.strip())
            buf = ""
        elif ch == "}":
            if stack:
                selector = stack[-1]
                at_rules = " ".join(a for a in stack[:-1] if a.startswith("@"))
                rules.append((selector, buf, at_rules))
                stack.pop()
            buf = ""
        else:
            buf += ch
    return rules


def _specificity(selector: str) -> tuple[int, int, int]:
    ids = len(re.findall(r"#[\w-]+", selector))
    classes = len(re.findall(r"\.[\w-]+|\[[^\]]*\]|:(?!:)[\w-]+", selector))
    types = len(re.findall(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)", selector))
    return (ids, classes, types)


def check_craft_regressions(css: str) -> None:
    """The two visible defects D1/D2 and the mobile measure D10, at the source level."""
    print("\n-- 11. craft regressions (B2-04 / D1, D2, D10) --")
    rules = _css_rules(css)
    hide: list[tuple[tuple[int, int, int], str]] = []
    show: list[tuple[tuple[int, int, int], str]] = []
    for selector, body, at_rules in rules:
        if "media" in at_rules:
            continue
        for one in selector.split(","):
            one = one.strip()
            if not one:
                continue
            if ".art-tall" in one and re.search(r"display\s*:\s*none", body):
                hide.append((_specificity(one), one))
            if "svg" in one and re.search(r"display\s*:\s*block", body):
                show.append((_specificity(one), one))
    check(bool(hide) and bool(show) and min(h[0] for h in hide) >= max(s[0] for s in show),
          "D1: the rule hiding the tall variant out-specifies every container rule that makes a "
          "figure SVG a block box (the exact specificity inversion that drew every diagram twice)",
          f"hide={sorted({h[0] for h in hide}, reverse=True)[:2]} "
          f"show={sorted({s[0] for s in show}, reverse=True)[:2]}"
          if hide and show else "no rule found")

    media = [r for r in rules if "max-width: 767.98px" in r[2]]
    m_hide = any(".art-wide" in sel and re.search(r"display\s*:\s*none", body)
                 for sel, body, _a in media)
    m_show = any(".art-tall" in sel and re.search(r"display\s*:\s*block", body)
                 for sel, body, _a in media)
    check(m_hide and m_show,
          "D1: below 768px the wide variant is hidden and the tall variant is shown, in the same "
          "specificity class")
    rank_rules = [(sel, body) for sel, body, a in rules
                  if "media" not in a and ".rank" in sel]
    check(bool(rank_rules) and not any(re.search(r"flex\s*:\s*0\s+1", body)
                                       for _s, body in rank_rules),
          "D2: the ordinal is not a shrinkable flex item")
    check(any(re.search(r"flex\s*:\s*none", body) for _s, body in rank_rules),
          "D2: .rank declares flex: none")
    check(any(re.search(r"white-space\s*:\s*nowrap", body) for _s, body in rank_rules),
          "D2: .rank cannot wrap its two digits")

    # B2-05b / N1 + N7 — the hero's `Focus`/`Languages` labels broke mid-word (FO / CU / S) because
    # `overflow-wrap: anywhere` sat on `body` (a one-character min-content width for every text
    # node) and `.glance-item` is a flex row whose `dt` could then be squeezed to ~2 characters.
    # Both halves are asserted at the source so the next component cannot meet the same class of
    # bug: the property must not be on `body`, and the label must not be a shrinkable flex item.
    body_wrap = [sel for sel, body, at in rules
                 if "media" not in at
                 and any(one.strip() == "body" for one in sel.split(","))
                 and re.search(r"overflow-wrap\s*:\s*(anywhere|break-word)", body)]
    check(not body_wrap,
          "N7: `overflow-wrap: anywhere` is not declared on `body` (a one-character min-content "
          "width is what lets any flex/grid row squeeze a label mid-word — the D2/N1 class)",
          f"body rules: {body_wrap}" if body_wrap else
          "the property is scoped to the token-bearing selectors only")
    scoped_wrap = [sel for sel, body, at in rules
                   if "media" not in at
                   and re.search(r"overflow-wrap\s*:\s*(anywhere|break-word)", body)
                   and not any(one.strip() == "body" for one in sel.split(","))]
    check(bool(scoped_wrap),
          "N7: the property is still declared where a long token actually needs it (scoping, not "
          "deletion)",
          f"{len(scoped_wrap)} scoped rule(s)")
    glance_flex = [sel for sel, body, _at in rules
                   if ".glance-item" in sel and "dt" not in sel and "dd" not in sel
                   and re.search(r"display\s*:\s*flex", body)]
    glance_dt = [(sel, body) for sel, body, at in rules
                 if "media" not in at and ".glance-item dt" in sel]
    check((not glance_flex) or bool(glance_dt and all(re.search(r"flex\s*:\s*none", b)
                                                     for _s, b in glance_dt)),
          "N1: the hero's attribute label cannot be squeezed by its own flex row — the label is a "
          "token, not a shrinkable flex item (`.glance-item dt` declares flex: none when "
          "`.glance-item` is a flex row)",
          f"flex-row rules={glance_flex}; dt rules={[s for s, _b in glance_dt]}")


def check_visible_provenance_tokens(docs: Path) -> None:
    """B2-04 / D5: the internal tier taxonomy is not on any page as visible text."""
    print("\n-- 12. provenance vocabulary is not published (D5) --")
    hits = []
    for page in sorted(docs.rglob("*.html")):
        html_ = page.read_text(encoding="utf-8")
        body = html_.split("<body", 1)[-1]
        text = re.sub(r"<[^>]+>", " ", body)
        for tok in re.findall(r"\bS[1235]\b", text):
            hits.append(f"{page.relative_to(docs)}: {tok}")
    check(not hits, "no rendered page shows a source-tier token (S1/S2/S3/S5) to the visitor",
          f"hits={hits[:5]}" if hits else "12 pages scanned, 0 tier tokens in visible text")
    check(any('data-source-tiers="S' in p.read_text(encoding="utf-8")
              for p in sorted(docs.rglob("*.html"))),
          "the tier taxonomy still reaches the DOM as data-source-tiers (the audit trail is intact)")


# --------------------------------------------------------------------------- 13. the shipped face

# B2-05b / N6 — the D6b token-name check used to grep the SHIPPED STYLESHEET only, so the canon on
# paper was unverified: the application kit kept a live `var(--font-human)` in its talk-title
# specimen (`design-kit/02-talk-title-slide.html:74`), a token that no longer exists, so the
# speaker's name on the canonical slide silently fell back to the inherited voice. The audit now
# covers the kit and the DNA documents too. Prose that *names* the retired token is not a use —
# the kits explain the retirement deliberately — so only a real use (`var(--font-human)` or a
# `--font-human:` declaration) is a hit.
DNA_DOCS = ("DESIGN_LANGUAGE.md", "DESIGN_SYSTEM.md", "ART_DIRECTION.md")
RETIRED_TOKEN_USE = re.compile(r"var\(\s*--font-human\s*\)|--font-human\s*:")
CANON_SUFFIXES = {".html", ".css", ".md", ".svg", ".txt"}


def _canon_targets(company: Path) -> list[Path]:
    targets: list[Path] = []
    kit = company / "design-kit"
    if kit.is_dir():
        targets += sorted(p for p in kit.rglob("*")
                          if p.is_file() and p.suffix.lower() in CANON_SUFFIXES)
    targets += [company / name for name in DNA_DOCS]
    return targets


def _retired_token_uses(company: Path) -> tuple[list[str], int]:
    """Live `--font-human` uses across the kit and the DNA documents, and how many files were read."""
    hits: list[str] = []
    scanned = 0
    for path in _canon_targets(company):
        if not path.is_file():
            hits.append(f"{path}: MISSING — the canon cannot be audited")
            continue
        scanned += 1
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if RETIRED_TOKEN_USE.search(line):
                hits.append(f"{path.name}:{i}: {line.strip()[:88]}")
    return hits, scanned


def check_shipped_face(docs: Path, css: str, company: Path) -> None:
    """B2-04 / D6: the identity is deliverable — a face is shipped, not borrowed from the OS."""
    print("\n-- 13. the display face is shipped (D6) --")
    faces = re.findall(r"@font-face\s*\{(.*?)\}", css, re.S)
    check(len(faces) >= 1, "the stylesheet declares at least one @font-face rule",
          f"{len(faces)} declared")
    srcs = []
    for face in faces:
        family = re.search(r'font-family:\s*"([^"]+)"', face)
        url = re.search(r'url\("([^"]+)"\)', face)
        display = re.search(r"font-display:\s*(\w+)", face)
        if family and url:
            srcs.append((family.group(1), url.group(1), display.group(1) if display else "-"))
    check(bool(srcs), "every @font-face names a family and a local src")
    check(all(u.startswith("/assets/") for _f, u, _d in srcs),
          "the font files are self-hosted under /assets/ (no third-party request)",
          f"{len(srcs)} faces: {[u for _f, u, _d in srcs]}")
    check(all(d == "swap" for _f, _u, d in srcs),
          "every shipped face uses font-display: swap (first paint is never blocked)")
    missing = [docs / u.lstrip("/") for _f, u, _d in srcs
               if not (docs / u.lstrip("/")).exists()
               or (docs / u.lstrip("/")).stat().st_size < 1024]
    check(not missing, "every declared font file exists in the published tree and is not empty",
          f"missing/empty: {[str(m) for m in missing]}" if missing else
          f"{len(srcs)} files, {sum((docs / u.lstrip('/')).stat().st_size for _f, u, _d in srcs) // 1024} KB total")
    shipped_families = {f for f, _u, _d in srcs}
    display_stack = re.search(r"--font-display:\s*([^;]+);", css)
    stack = display_stack.group(1) if display_stack else ""
    check(any(f'"{fam}"' in stack for fam in shipped_families),
          "--font-display LEADS with the shipped family (the system stack is a fallback, not the "
          "identity)", stack.strip()[:90])
    check("--font-human" not in css,
          "D6b: one token name for the display voice (--font-human is retired in the stylesheet)")
    canon_hits, canon_scanned = _retired_token_uses(company)
    check(not canon_hits,
          "D6b: the retirement holds across the canon too — 0 live `--font-human` uses in the "
          "application kit and the DNA documents",
          f"{len(canon_hits)} live use(s): {canon_hits[:3]}" if canon_hits else
          f"{canon_scanned} kit/DNA files scanned (html, css, md, svg, txt)")
    # the subset must not be the whole face: shipping 300 KB to serve four glyph roles is the
    # performance defect D0 that D6 must not re-introduce
    if srcs:
        biggest = max((docs / u.lstrip("/")).stat().st_size for _f, u, _d in srcs)
        check(biggest < 120 * 1024, "the shipped face is a subset, not the full font file (D0)",
              f"largest file {biggest // 1024} KB")
    else:
        # no face is declared at all: report it here instead of crashing on an empty sequence,
        # so this file can also be run against a revision that predates the shipped face.
        check(False, "the shipped face is a subset, not the full font file (D0)",
              "no @font-face to measure — the stylesheet declares no face")


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--css", default="docs/assets/styles.css")
    ap.add_argument("--ledger", default="/root/company/BENCHMARK_01/FACTS_LEDGER.md")
    # B2-05b / N6: the canon — the application kit and the DNA documents — is part of the same
    # audit (token names must be one name everywhere the language is written down). It defaults to
    # the company directory that holds the ledger, so the check keeps working from any checkout.
    ap.add_argument("--company", default=None,
                    help="company directory holding design-kit/ and the DNA documents "
                         "(default: the ledger's directory)")
    args = ap.parse_args()

    docs = Path(args.docs).resolve()
    company = Path(args.company).resolve() if args.company else Path(args.ledger).resolve().parent
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
    check_evidence_objects(docs)
    check_craft_regressions(css)
    check_visible_provenance_tokens(docs)
    check_shipped_face(docs, css, company)

    print("\n" + "=" * 78)
    print(f"checks run: {CHECKS}   failures: {len(FAILURES)}")
    for f in FAILURES:
        print("  FAILED: " + f)
    print("DESIGN CHECKS RESULT: " + ("PASS" if not FAILURES else "FAIL"))
    print("=" * 78)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
