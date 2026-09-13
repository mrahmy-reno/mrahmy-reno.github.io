#!/usr/bin/env python3
"""Original schematic artefacts for the redesign (PROOF_PLAN.md P-0 … P-10).

Stdlib only. Every artefact is an inline SVG whose every label is a phrase the FACTS_LEDGER
already prints (or a structural connective word), so a diagram can never introduce a fact.

Rendering contract (DESIGN_SYSTEM.md §6.4 / §6.8, PROOF_PLAN.md §4):
  * geometry carries no meaning: no axis, no bar, no gauge, no tick count, no number;
  * colour and weight come from the stylesheet (classes only) — no literal colour here;
  * the final geometry is present in the markup; a reveal may only animate opacity;
  * each artefact is drawn twice — a landscape schematic (>=768px) and the same nodes
    relaid as a vertical rail (<768px) — with identical labels. CSS toggles which one
    is displayed; `aria-hidden` keeps the hidden copy out of the accessibility tree.
"""

from __future__ import annotations

import html
import re

__all__ = ["artefact_pair", "system_map_pair", "ARTEFACT_META"]

PAD = 16.0
WIDE_W = 1000.0
TALL_W = 400.0
BOX_GAP = 20.0
LINE_H = 19.0
FS = 14.0
CH_W = 9.4          # measured advance per character at 14px mono + 0.06em tracking
TALL_CHARS = 34     # the vertical rail's per-line character budget


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def wrap(text: str, max_chars: int) -> list[str]:
    """Greedy word wrap that prefers a real boundary over a mid-word break.

    A token longer than the line budget is broken at its last `/` (then `-`) inside the budget,
    so a compound label such as `contract/adversarial/compliance suites` breaks into whole words
    and never into fragments — the label-diff audit in tests/design_checks.py depends on this.
    """
    lines: list[str] = []

    def push(chunk: str) -> None:
        if lines and len(lines[-1]) + 1 + len(chunk) <= max_chars and not lines[-1].endswith("/"):
            lines[-1] = f"{lines[-1]} {chunk}"
        else:
            lines.append(chunk)

    for word in text.split():
        while len(word) > max_chars:
            cut = word.rfind("/", 0, max_chars + 1)
            keep = 1
            if cut < 1:
                cut = word.rfind("-", 1, max_chars + 1)
                keep = 0
            if cut < 1:
                cut = max_chars
                keep = 0
            push(word[:cut + keep])
            word = word[cut + 1:]
        push(word)
    return lines or [""]


class Canvas:
    """Accumulates SVG primitives with a deterministic, attribute-quoted shape."""

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        self.parts: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def rect(self, x, y, w, h, cls, rx=8.0) -> None:
        self.add(f'<rect class="{cls}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
                 f'rx="{rx:g}" />')

    def line(self, x1, y1, x2, y2, cls) -> None:
        self.add(f'<line class="{cls}" x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" />')

    def text(self, x, y, text, cls="dg-label", anchor="middle") -> None:
        self.add(f'<text class="{cls}" x="{x:g}" y="{y:g}" text-anchor="{anchor}">'
                 f'{esc(text)}</text>')

    def node(self, x, y, w, h, lines, cls="dg-box", label_cls="dg-label") -> None:
        """A labelled node: a rounded rect with its label vertically centred."""
        self.rect(x, y, w, h, cls)
        cx = x + w / 2
        first = y + h / 2 - (len(lines) - 1) * LINE_H / 2 + FS * 0.34
        for i, line in enumerate(lines):
            self.text(cx, first + i * LINE_H, line, label_cls)

    def svg(self, uid: str, title: str, desc: str, extra_class: str,
            role: str = "img") -> str:
        return (f'<svg class="dg {extra_class}" viewBox="0 0 {self.width:g} {self.height:g}" '
                f'role="{role}" aria-labelledby="{uid}-t {uid}-d" '
                f'preserveAspectRatio="xMidYMid meet">\n'
                f'  <title id="{uid}-t">{esc(title)}</title>\n'
                f'  <desc id="{uid}-d">{esc(desc)}</desc>\n'
                + "\n".join(f"  {p}" for p in self.parts)
                + "\n</svg>")


# --------------------------------------------------------------------------- labels

def _unit(label: str, kind: str = "node", signal: bool = False,
          band: list[str] | None = None) -> dict:
    return {"label": label, "kind": kind, "signal": signal, "band": band}


def _units_height(units: list[dict], chars: int) -> float:
    lines = max(len(wrap(u["label"], chars)) for u in units)
    return 2 * PAD + (lines - 1) * LINE_H


# --------------------------------------------------------------------------- rail

def rail(units: list[dict], uid: str, title: str, desc: str, tail: str = "") -> tuple[str, str]:
    """Landscape stage rail + the same nodes as a vertical rail. Returns (wide, tall)."""
    stages = [u for u in units if u["kind"] != "note"]
    notes = [u for u in units if u["kind"] == "note"]

    # ---- landscape ---------------------------------------------------------
    n = len(stages)
    avail = WIDE_W - 2 * PAD
    box_w = min(184.0, (avail - (n - 1) * BOX_GAP) / n)
    chars = max(8, int(box_w / CH_W) - 1)
    box_h = _units_height(stages, chars)
    height = 2 * PAD + box_h + (2 * PAD + 34.0 if notes else 0.0)
    c = Canvas(WIDE_W, height)
    y = PAD
    total = n * box_w + (n - 1) * BOX_GAP
    x = (WIDE_W - total) / 2
    centres = []
    for i, unit in enumerate(stages):
        lines = wrap(unit["label"], chars)
        cls = {"node": "dg-box", "gate": "dg-gate", "source": "dg-box dg-src"}.get(unit["kind"],
                                                                                   "dg-box")
        c.node(x, y, box_w, box_h, lines, cls)
        centres.append(x + box_w / 2)
        if i < n - 1:
            c.line(x + box_w + 2, y + box_h / 2, x + box_w + BOX_GAP - 2, y + box_h / 2,
                   "dg-signal" if unit.get("signal") else "dg-edge")
        x += box_w + BOX_GAP
    if tail:
        c.text(WIDE_W - PAD, PAD - 4, tail, "dg-label-meta", anchor="end")
    if notes:
        ny = PAD + box_h + 2 * PAD
        c.text(PAD, ny - 6, "annotations", "dg-label-meta", anchor="start")
        nx = PAD
        for unit in notes:
            lines = wrap(unit["label"], 28)
            w = min(300.0, max(120.0, max(len(l) for l in lines) * CH_W + 24))
            c.node(nx, ny, w, 30.0, lines, "dg-note", "dg-label-meta")
            nx += w + 12
    wide = c.svg(uid, title, desc, "art-wide")

    # ---- tall (identical labels, vertical rail) ----------------------------
    t = Canvas(TALL_W, 0.0)
    y = PAD
    for i, unit in enumerate(stages):
        lines = wrap(unit["label"], TALL_CHARS)
        h = 2 * PAD + (len(lines) - 1) * LINE_H
        cls = {"node": "dg-box", "gate": "dg-gate", "source": "dg-box dg-src"}.get(unit["kind"],
                                                                                   "dg-box")
        t.node(PAD, y, TALL_W - 2 * PAD, h, lines, cls)
        y += h
        if i < n - 1:
            t.line(TALL_W / 2, y + 2, TALL_W / 2, y + BOX_GAP - 2,
                   "dg-signal" if unit.get("signal") else "dg-edge")
            y += BOX_GAP
    if notes:
        y += 16
        t.text(PAD, y, "annotations", "dg-label-meta", anchor="start")
        y += 10
    for unit in notes:
        lines = wrap(unit["label"], TALL_CHARS)
        h = 2 * PAD + (len(lines) - 1) * LINE_H
        t.node(PAD, y, TALL_W - 2 * PAD, h, lines, "dg-note", "dg-label-meta")
        y += h + 8
    t.height = y + PAD
    tall = t.svg(uid + "-v", title, desc, "art-tall")
    return wide, tall


# --------------------------------------------------------------------------- hub

def hub(centre: str, band: str, band_notes: list[str], bus: str, bus_side: str, lane: str,
        uid: str, title: str, desc: str) -> tuple[str, str]:
    """A hub with a scope band above, a bus below and a trace lane at the bottom."""
    c = Canvas(WIDE_W, 400.0)
    band_lines = wrap(band, 30)
    band_h = 2 * PAD + (len(band_lines) - 1) * LINE_H
    c.node(PAD, PAD, 460.0, band_h, band_lines, "dg-banner")
    nx = PAD + 470.0
    for note in band_notes:
        lines = wrap(note, 24)
        w = max(150.0, max(len(l) for l in lines) * CH_W + 24)
        h = 2 * PAD + (len(lines) - 1) * LINE_H
        c.node(nx, PAD, min(w, WIDE_W - PAD - nx), h, lines, "dg-note", "dg-label-meta")
        nx += w + 12

    hub_y = PAD + band_h + 56.0
    hub_w, hub_h = 260.0, 30.0 + 2 * PAD
    hub_x = (WIDE_W - hub_w) / 2
    c.line(WIDE_W / 2, PAD + band_h + 4, WIDE_W / 2, hub_y - 4, "dg-edge")
    c.node(hub_x, hub_y, hub_w, hub_h, wrap(centre, 26))

    bus_y = hub_y + hub_h + 56.0
    c.line(WIDE_W / 2, hub_y + hub_h + 4, WIDE_W / 2, bus_y - 4, "dg-signal")
    bus_w = 420.0
    bus_x = (WIDE_W - bus_w) / 2 - 90.0
    c.node(bus_x, bus_y, bus_w, 30.0 + 2 * PAD, wrap(bus, 34))
    side_w = 240.0
    c.line(bus_x + bus_w + 4, bus_y + 15 + PAD / 2, bus_x + bus_w + 40, bus_y + 15 + PAD / 2,
           "dg-edge")
    c.node(bus_x + bus_w + 44, bus_y, side_w, 30.0 + 2 * PAD, wrap(bus_side, 20),
           "dg-note", "dg-label-meta")

    lane_y = bus_y + 60.0 + PAD
    c.text(PAD, lane_y - 8, lane, "dg-label-meta", anchor="start")
    c.line(PAD, lane_y + 6, WIDE_W - PAD, lane_y + 6, "dg-edge")
    wide = c.svg(uid, title, desc, "art-wide")
    tall = _vrail_svg([_unit(centre), _unit(band), *[_unit(n, "note") for n in band_notes],
                       _unit(bus), _unit(bus_side, "note"), _unit(lane)], uid, title, desc)
    return wide, tall


# --------------------------------------------------------------------------- surfaces

def surfaces(items: list[dict], uid: str, title: str, desc: str) -> tuple[str, str]:
    """Two or three abstract surface shapes side by side, plus a connecting rail."""
    c = Canvas(WIDE_W, 340.0)
    n = len(items)
    avail = WIDE_W - 2 * PAD
    w = min(300.0, (avail - (n - 1) * 24.0) / n)
    x = (WIDE_W - (n * w + (n - 1) * 24.0)) / 2
    rail_label = items[0].get("rail", "end to end") if n >= 2 else ""
    for item in items:
        lines = wrap(item["label"], max(10, int(w / CH_W) - 2))
        h = 90.0
        c.text(x + w / 2, PAD + 6, item["caption"], "dg-label-meta")
        c.rect(x, PAD + 16, w, h, "dg-shape")
        first = PAD + 16 + h / 2 - (len(lines) - 1) * LINE_H / 2 + FS * 0.34
        for i, line in enumerate(lines):
            c.text(x + w / 2, first + i * LINE_H, line, "dg-label")
        for extra in item.get("extra", []):
            c.text(x + w / 2, PAD + 16 + h + 22, extra, "dg-label-meta")
        if item.get("rule"):
            c.line(x + 12, PAD + 16 + h + 34, x + w - 12, PAD + 16 + h + 34, "dg-boundary")
            c.line(x + w - 12, PAD + 16 + h + 34, x + w - 12, PAD + 16 + h + 26, "dg-boundary")
        x += w + 24.0
    if n >= 2:
        y = 300.0
        c.line(60.0, y, WIDE_W - 60.0, y, "dg-edge")
        c.text(WIDE_W / 2, y - 8, rail_label, "dg-label-meta")
    wide = c.svg(uid, title, desc, "art-wide")

    # the vertical rail carries the same labels, in the same reading order:
    # each surface's caption, its label, its annotations, then the joining rail.
    units: list[dict] = []
    for item in items:
        units.append(_unit(item["caption"], "note"))
        units.append(_unit(item["label"]))
        for extra in item.get("extra", []):
            units.append(_unit(extra, "note"))
    if rail_label:
        units.append(_unit(rail_label, "note"))
    tall = _vrail_svg(units, uid, title, desc)
    return wide, tall


def _vrail_svg(units: list[dict], uid: str, title: str, desc: str) -> str:
    t = Canvas(TALL_W, 0.0)
    y = PAD
    for i, unit in enumerate(units):
        lines = wrap(unit["label"], TALL_CHARS)
        h = 2 * PAD + (len(lines) - 1) * LINE_H
        cls = {"node": "dg-box", "gate": "dg-gate", "source": "dg-box dg-src",
               "note": "dg-note"}.get(unit["kind"], "dg-box")
        t.node(PAD, y, TALL_W - 2 * PAD, h, lines, cls,
               "dg-label-meta" if unit["kind"] == "note" else "dg-label")
        y += h
        if i < len(units) - 1:
            t.line(TALL_W / 2, y + 2, TALL_W / 2, y + BOX_GAP - 2, "dg-edge")
            y += BOX_GAP
    t.height = y + PAD
    return t.svg(uid + "-v", title, desc, "art-tall")


# --------------------------------------------------------------------------- system map

DOMAINS = [
    ("Security operations & agent safety", ["sama-soc-triage", "smartops-soc-app",
                                            "milo-ai-employee", "pulsesec"]),
    ("Applied RAG & analytics", ["tonsy-gpt", "smart-care"]),
    ("Shipped products & ML systems", ["halalbot", "forwheelz", "email-mcp",
                                       "voice-agent-core"]),
]


def system_map(projects: dict[str, str], uid: str, title: str, desc: str) -> tuple[str, str]:
    """P-0: the ten projects in three domain bands, every node a real link."""
    rows = [(name, [(slug, projects[slug]) for slug in slugs]) for name, slugs in DOMAINS]
    # ---- landscape ---------------------------------------------------------
    c = Canvas(WIDE_W, 360.0)
    y = PAD
    for domain, nodes in rows:
        c.text(PAD, y + 14, domain, "dg-label-meta", anchor="start")
        nx = PAD
        ny = y + 26
        avail = WIDE_W - 2 * PAD
        w = min(210.0, (avail - (len(nodes) - 1) * 12.0) / len(nodes))
        for slug, name in nodes:
            lines = wrap(name, max(9, int(w / CH_W) - 1))
            h = 2 * PAD + (len(lines) - 1) * LINE_H
            c.add(f'<a href="/projects/{slug}.html" class="dg-link">')
            c.node(nx, ny, w, h, lines, "dg-box", "dg-label-meta")
            c.add("</a>")
            nx += w + 12.0
        c.line(PAD, ny + 62, WIDE_W - PAD, ny + 62, "dg-rule")
        y = ny + 74
    c.height = y
    # role="group", not "img": the map's nodes are real links, and a widget role may not
    # contain focusable descendants (axe: nested-interactive).
    wide = c.svg(uid, title, desc, "art-wide", role="group")
    # ---- vertical rail -----------------------------------------------------
    t = Canvas(TALL_W, 0.0)
    y = PAD
    for domain, nodes in rows:
        t.text(PAD, y + 10, domain, "dg-label-meta", anchor="start")
        y += 20
        for slug, name in nodes:
            lines = wrap(name, 32)
            h = 2 * PAD + (len(lines) - 1) * LINE_H
            t.add(f'<a href="/projects/{slug}.html" class="dg-link">')
            t.node(PAD, y, TALL_W - 2 * PAD, h, lines, "dg-box", "dg-label-meta")
            t.add("</a>")
            y += h + 10
        y += 10
    t.height = y
    tall = t.svg(uid + "-v", title, desc, "art-tall", role="group")
    return wide, tall


# --------------------------------------------------------------------------- trace (B2-04)
#
# The B2-03 critique's central finding (D3): every artefact was a stack of large outlined boxes
# each holding one 1-3-word label, so all 13 drew the same object, and the index's "Work, shown"
# plane drew the ten project *names*. The trace model answers that with the structure of a real
# run: the project's own stages left to right with typed edges, a stage that is a SET bracketed
# with its own properties, a boundary rule the path sits behind, a trace lane beneath, and
# cross-cutting annotation rows that span every stage instead of sitting between two of them
# (D7: typed contracts / grounding controls are properties of the project, not inter-stage gates).
#
# Geometry still carries no quantity: the band is one set, not a count, and there is no axis,
# bar, gauge, tick count or number anywhere. Every label is a ledger phrase or a declared
# structural word — audited by tests/design_checks.py section 6.

def trace(stages: list[dict], uid: str, title: str, desc: str, *, crosscut: dict | None = None,
          band: dict | None = None, boundary: str | None = None, notes: list[str] | None = None,
          lane: str | None = None) -> tuple[str, str]:
    """A run trace (landscape) + the same labels relaid as a vertical rail.

    stages   : [{"label", kind?, signal?, band?: [labels]}] — band labels are the stage's own
               properties, drawn as a bracketed set under that stage.
    crosscut : {"items": [labels]} — drawn as a row ABOVE the whole rail, bracketed down onto
               three points of it, so the reader sees them applying to every stage.
    boundary : a dashed rule across the diagram with its label at the left.
    notes    : annotation boxes under the rail.
    lane     : a labelled lane closing the bottom of the diagram.
    """
    units: list[dict] = []          # the tall variant's reading order, filled as we draw
    c = Canvas(WIDE_W, 0.0)
    avail = WIDE_W - 2 * PAD
    n = len(stages)
    box_w = min(184.0, (avail - (n - 1) * BOX_GAP) / n)
    chars = max(8, int(box_w / CH_W) - 1)
    box_h = _units_height(stages, chars)

    y = PAD
    if crosscut:
        items = crosscut["items"]
        units.append(_unit("annotations", "note"))
        c.text(PAD, y + 11, "annotations", "dg-label-meta", anchor="start")
        y += 20.0
        iw = (avail - (len(items) - 1) * 12.0) / len(items)
        iw_chars = max(8, int(iw / CH_W) - 1)
        ch = max(_units_height([_unit(i) for i in items], iw_chars), 2 * PAD)
        for i, label in enumerate(items):
            units.append(_unit(label, "note"))
            c.node(PAD + i * (iw + 12.0), y, iw, ch, wrap(label, iw_chars), "dg-note",
                   "dg-label-meta")
        y += ch + 6.0
        # the bracket: one rule under the row, ticked down onto the rail at three points
        c.line(PAD, y, WIDE_W - PAD, y, "dg-rule")
        for i in range(3):
            xx = PAD + avail * (i + 1) / 4.0
            c.line(xx, y, xx, y + 14.0, "dg-rule")
        y += 26.0

    y_rail = y
    total = n * box_w + (n - 1) * BOX_GAP
    x0 = (WIDE_W - total) / 2
    centres = [x0 + i * (box_w + BOX_GAP) + box_w / 2 for i in range(n)]
    for i, unit in enumerate(stages):
        lines = wrap(unit["label"], chars)
        cls = {"node": "dg-box", "gate": "dg-gate", "source": "dg-box dg-src"}.get(
            unit.get("kind", "node"), "dg-box")
        units.append(_unit(unit["label"], unit.get("kind", "node"), unit.get("signal", False)))
        c.node(x0 + i * (box_w + BOX_GAP), y_rail, box_w, box_h, lines, cls)
        if i < n - 1:
            c.line(x0 + i * (box_w + BOX_GAP) + box_w + 2, y_rail + box_h / 2,
                   x0 + (i + 1) * (box_w + BOX_GAP) - 2, y_rail + box_h / 2,
                   "dg-signal" if unit.get("signal") else "dg-edge")
    y = y_rail + box_h

    for i, unit in enumerate(stages):
        sub = unit.get("band")
        if not sub:
            continue
        bx = x0 + i * (box_w + BOX_GAP)
        lines = [ln for label in sub for ln in wrap(label, chars)]
        bh = 2 * PAD + (len(lines) - 1) * LINE_H
        c.line(bx + box_w * 0.3, y + 2, bx + box_w * 0.3, y + 20, "dg-edge")
        c.line(bx + box_w * 0.7, y + 20, bx + box_w * 0.7, y + 2, "dg-edge")
        c.node(bx, y + 20, box_w, bh, lines, "dg-note", "dg-label-meta")
        units.extend(_unit(label, "note") for label in sub)
        y += 20 + bh

    if boundary:
        y += 22.0
        units.append(_unit(boundary, "note"))
        c.text(PAD, y - 6, boundary, "dg-label-meta", anchor="start")
        c.add(f'<line class="dg-boundary dg-dashed" x1="{PAD:g}" y1="{y:g}" '
              f'x2="{WIDE_W - PAD:g}" y2="{y:g}" />')
        y += 6.0

    if notes:
        y += 30.0
        units.append(_unit("annotations", "note"))
        c.text(PAD, y - 10, "annotations", "dg-label-meta", anchor="start")
        nx = PAD
        nh = 0.0
        boxes: list[tuple[float, float, float, list[str]]] = []
        for label in notes:
            lines = wrap(label, 28)
            w = min(300.0, max(120.0, max(len(ln) for ln in lines) * CH_W + 24))
            h = 2 * PAD + (len(lines) - 1) * LINE_H
            nh = max(nh, h)
            boxes.append((nx, w, h, lines))
            nx += w + 12.0
        for bx, w, h, lines in boxes:
            units.append(_unit(" ".join(lines), "note"))
            c.node(bx, y, w, h, lines, "dg-note", "dg-label-meta")
        y += nh

    if lane:
        y += 26.0
        units.append(_unit(lane, "note"))
        c.text(PAD, y - 8, lane, "dg-label-meta", anchor="start")
        c.line(PAD, y + 6, WIDE_W - PAD, y + 6, "dg-edge")
        y += 10.0

    c.height = y + PAD
    wide = c.svg(uid, title, desc, "art-wide")
    tall = _vrail_svg(units, uid, title, desc)
    return wide, tall


# --------------------------------------------------------------------------- typed contract (B2-04)
#
# The second object type the B2-03 critique named as missing (D3): "a schema or typed-contract
# excerpt". It is drawn as a code surface — a header line, field rows, a gutter — not as a stack
# of boxes with one label each, so it is visibly a different kind of object from a schematic.
# The field names are the ledger's own nouns; types, values and counts are omitted, which is what
# the caption says.

def contract(uid: str, title: str, desc: str, *, head: str, rows: list[str],
             notes: list[str]) -> tuple[str, str]:
    left_w = 600.0
    right_x = PAD + left_w + 20.0
    right_w = WIDE_W - PAD - right_x
    left_h = 2 * PAD + 22.0 + len(rows) * 26.0

    c = Canvas(WIDE_W, 0.0)
    c.rect(PAD, PAD, left_w, left_h, "dg-shape")
    c.text(PAD + 20.0, PAD + PAD + 6.0, head, "dg-label", anchor="start")
    c.line(PAD + 14.0, PAD + PAD + 18.0, PAD + left_w - 14.0, PAD + PAD + 18.0, "dg-rule")
    for i, row in enumerate(rows):
        ry = PAD + PAD + 18.0 + (i + 1) * 26.0
        c.line(PAD + 16.0, ry - 5.0, PAD + 28.0, ry - 5.0, "dg-edge")
        c.text(PAD + 40.0, ry, row, "dg-label-meta", anchor="start")
        if i < len(rows) - 1:
            c.line(PAD + 14.0, ry + 9.0, PAD + left_w - 14.0, ry + 9.0, "dg-rule")

    ny = PAD
    for label in notes:
        lines = wrap(label, max(8, int(right_w / CH_W) - 1))
        h = 2 * PAD + (len(lines) - 1) * LINE_H
        c.node(right_x, ny, right_w, h, lines, "dg-note", "dg-label-meta")
        ny += h + 8.0
    c.height = max(PAD + left_h, ny) + PAD

    wide = c.svg(uid, title, desc, "art-wide")
    tall = _vrail_svg([_unit(head)] + [_unit(r) for r in rows]
                      + [_unit(note, "note") for note in notes], uid, title, desc)
    return wide, tall


# --------------------------------------------------------------------------- figures

def figure(uid: str, wide: str, tall: str, caption: str, scope: str) -> str:
    return (f'<figure class="artefact">\n'
            f'  <div class="artefact-frame">\n{_indent(wide, 2)}\n{_indent(tall, 2)}\n  </div>\n'
            f'  <figcaption>{esc(caption)}</figcaption>\n'
            f'  <p class="scope-caption">{esc(scope)}</p>\n'
            f'</figure>')


def _indent(markup: str, level: int) -> str:
    pad = "  " * level
    return "\n".join(pad + line for line in markup.splitlines())


CAPTION = "Schematic — structure only. No operational data."
CAPTION_SHAPES = "Schematic wireframe shapes — not screenshots. No operational data."
CAPTION_INTERFACE = "Schematic — interface shape only."

# --------------------------------------------------------------------------- catalogue

ARTEFACT_META: dict[str, dict] = {
    "system-map": {
        "title": "System map — ten projects in three domains",
        "desc": ("Ten project nodes grouped into three structural domains: security operations & "
                 "agent safety; applied RAG & analytics; shipped products & ML systems. Project "
                 "names are the ledger's own; the grouping is structural. Structure only — no "
                 "counts, no ranking, no volume."),
        "caption": "Ten projects — how they fit together.",
        "scope": CAPTION,
    },
    "sama-soc-triage": {
        # B2-04 / D7 repair: the previous artefact asserted a SIX-element ordered chain and put
        # "typed contracts" / "grounding/evidence controls" BETWEEN stages. The ledger names
        # exactly five workflow components for SAMA and lists those two as properties of the
        # project, so they are drawn here as cross-cutting annotations ABOVE the rail, and the
        # rail carries the ledger's five components in the ledger's own order.
        "title": "SAMA — one triage run",
        "desc": ("One triage run, drawn left to right: the ledger's five workflow components in "
                 "the ledger's own order — context construction, active investigation, threat "
                 "modeling, quality guards, verdict generation — with typed contracts and "
                 "grounding/evidence controls drawn as cross-cutting annotations above the whole "
                 "run (they are properties of the project, not gates between stages), and the "
                 "evaluation surfaces the role names as annotations beneath the verdict. "
                 "Structure only — no counts, no timestamps."),
        "caption": "One triage run: the ledger's five stages, controls across all of them, evaluation at the verdict.",
        "scope": CAPTION,
        "model": "trace",
        "stages": [
            _unit("context construction"), _unit("active investigation"),
            _unit("threat modeling"), _unit("quality guards"),
            _unit("verdict generation", signal=True),
        ],
        "crosscut": {"items": ["typed contracts", "grounding/evidence controls"]},
        "notes": ["LLM-as-judge", "RAGAS", "blind-vs-shown",
                  "contract/adversarial/compliance suites"],
        "second": "typed-contract",
    },
    "typed-contract": {
        # B2-04 / D3: the object type the critique named as missing — a typed-contract excerpt,
        # drawn as a code surface rather than a chain of boxes. Field names are the ledger's own
        # nouns for this project; types, values and counts are omitted (see the caption).
        "title": "The verdict's contract, as a shape",
        "desc": ("A typed-contract excerpt drawn as a code surface: the verdict generation "
                 "interface, the four controls bound to it (evidence, grounding/evidence "
                 "controls, quality guards, typed contracts) and the evaluation surfaces that "
                 "sit on it. Field types, field names and values are omitted; the shape is "
                 "structural."),
        "caption": "The verdict's contract, as a shape.",
        "scope": CAPTION_INTERFACE,
        "model": "contract",
        "head": "verdict generation",
        "rows": ["evidence", "grounding/evidence controls", "quality guards", "typed contracts"],
        "notes": ["LLM-as-judge", "RAGAS", "blind-vs-shown",
                  "contract/adversarial/compliance suites"],
    },
    "smartops-soc-app": {
        "title": "SmartOps SOC App — a brokered investigation run",
        "desc": ("A task broker coordinating the domain-analyst set — the set carries "
                 "hypothesis-blind analysis and scope as its own bracketed properties — whose "
                 "findings flow into evidence-linked findings, with VirusTotal enrichment as an "
                 "annotation and a replayable traces lane closing the diagram. Structure only — "
                 "no counts, no timestamps."),
        "caption": "A brokered investigation run: broker, the analyst set, evidence-linked findings, trace lane.",
        "scope": CAPTION,
        "model": "trace",
        "stages": [
            _unit("task broker"),
            _unit("domain analysts", "node", False, ["hypothesis-blind analysis", "scope"]),
            _unit("evidence-linked findings", signal=True),
        ],
        "notes": ["VirusTotal enrichment"],
        "lane": "replayable traces",
    },
    "milo-ai-employee": {
        "title": "Milo — approval binding behind the authority boundary",
        "desc": ("A request path through a safety-first agentic operations teammate to a "
                 "proposed action — the action carries budget/time limits and redaction as its "
                 "own bracketed properties — then approval binding (the gate), then controlled "
                 "write-back. A dashed authority boundaries rule crosses the diagram, and "
                 "idempotent actions and reconciliation close it as a lane. Source material is "
                 "simulated."),
        "caption": "Approval binding and the authority boundary, on one request path.",
        "scope": CAPTION,
        "model": "trace",
        "stages": [
            _unit("request"), _unit("safety-first agentic operations teammate"),
            _unit("proposed action", "node", False, ["budget/time limits", "redaction"]),
            _unit("approval binding", "gate"), _unit("controlled write-back", "node", True),
        ],
        "boundary": "authority boundaries",
        "notes": ["simulated Splunk/Cribl incidents"],
        "lane": "idempotent actions and reconciliation",
    },
    "pulsesec": {
        "title": "PulseSec — domain packs, connectors and the trace lane",
        "desc": ("A multi-domain investigation copilot whose domain-pack architecture carries its "
                 "MCP connectors as a bracketed set, then schema-grounded query generation, then "
                 "the React/Vite UI. A dashed guardrails rule crosses the diagram and the "
                 "agent-trace telemetry lane closes it."),
        "caption": "Domain packs, connectors, grounded queries and the trace lane.",
        "scope": CAPTION,
        "model": "trace",
        "stages": [
            _unit("multi-domain investigation copilot"),
            _unit("domain-pack architecture", "node", False, ["MCP connectors"]),
            _unit("schema-grounded query generation"),
            _unit("React/Vite UI", "node", True),
        ],
        "boundary": "guardrails",
        "lane": "agent-trace telemetry, timeline/case handling",
    },
    "tonsy-gpt": {
        "title": "Tonsy-GPT — hybrid retrieval pipeline",
        "desc": ("A query with parent-setting expansion fans out to BM25 and ChromaDB, merges at "
                 "RRF, passes neural reranking and a semantic caching side channel, then "
                 "FastAPI/SSE and Next.js, with session persistence on the response leg."),
        "caption": "Hybrid retrieval: fan-out, fusion, reranking, caching.",
        "scope": CAPTION,
        "model": "rail",
        "units": [
            _unit("query"), _unit("parent-setting expansion", "note"),
            _unit("BM25"), _unit("ChromaDB"), _unit("RRF"),
            _unit("neural reranking"), _unit("semantic caching"), _unit("FastAPI/SSE"),
            _unit("Next.js", signal=True), _unit("session persistence", "note"),
        ],
    },
    "smart-care": {
        "title": "Smart Care — intent to grounded output",
        "desc": ("A staged rail from intent to grounded SQL to stats to visualisation agents, "
                 "with an orchestrator and shared state as the spine, schema-aware prompting and "
                 "session memory as annotations, Dremio as the source layer and a streaming React "
                 "UI as the final surface."),
        "caption": "Intent to grounded output.",
        "scope": CAPTION,
        "model": "rail",
        "units": [
            _unit("intent"), _unit("grounded SQL"), _unit("stats"),
            _unit("visualisation agents", signal=True),
            _unit("orchestrator + shared state", "note"),
            _unit("schema-aware prompting", "note"), _unit("session memory", "note"),
            _unit("Dremio", "note"), _unit("streaming React UI", "note"),
        ],
    },
    "halalbot": {
        "title": "HalalBot — shipped surfaces",
        "desc": ("Two abstract surface shapes — a customer conversation surface with "
                 "Arabic/English parsing, and an operations surface — joined by the live tunnel "
                 "end-to-end path, plus a release path from mobile packaging to a signed Android "
                 "APK marked by a tick rule. Abstract shapes, not screenshots."),
        "caption": "Shipped surfaces: conversation, operations, release path.",
        "scope": CAPTION_SHAPES,
        "model": "surfaces",
        "items": [
            {"caption": "customer conversation surface",
             "label": "shipped WhatsApp ordering product",
             "extra": ["Arabic/English parsing"], "rail": "live tunnel E2E"},
            {"caption": "operations surface", "label": "owner dashboard"},
            {"caption": "release path", "label": "mobile packaging → signed Android APK",
             "rule": True},
        ],
    },
    "forwheelz": {
        "title": "ForWheelz — feature pipeline to output contract",
        "desc": ("Vehicle telemetry through a trip pipeline to feature ablation and RF/XGBoost, "
                 "with error analysis as a side branch feeding back to feature ablation, and an "
                 "output contract block listing confidence, risk contributors, risk-index, "
                 "DNA-score and insurer/API integration."),
        "caption": "Telemetry to output contract.",
        "scope": CAPTION,
        "model": "rail",
        "units": [
            _unit("vehicle telemetry"), _unit("trip pipeline"), _unit("feature ablation"),
            _unit("RF/XGBoost"), _unit("output contract", signal=True),
            _unit("error analysis", "note"), _unit("confidence", "note"),
            _unit("risk contributors", "note"), _unit("risk-index", "note"),
            _unit("DNA-score", "note"), _unit("insurer/API integration", "note"),
        ],
    },
    "email-mcp": {
        "title": "email-MCP — tool-server surface",
        "desc": ("An MCP tool server with a documented tool-slot band. The slots are "
                 "generically labelled because the ledger does not name the tools. Interface "
                 "shape only."),
        "caption": "Tool-server surface.",
        "scope": CAPTION_INTERFACE,
        "model": "surfaces",
        "items": [
            {"caption": "server", "label": "MCP tool server", "extra": ["documented"]},
            {"caption": "tool slot", "label": "tool", "extra": ["documented"]},
            {"caption": "tool slot", "label": "tool", "extra": ["documented"]},
        ],
    },
    "voice-agent-core": {
        "title": "Voice agent core — the audio pipeline",
        "desc": ("A linear rail VAD, Whisper, LLM, TTS, with Arabic + English as a language band "
                 "spanning the rail and a terminal boundary labelled Twilio-ready."),
        "caption": "The audio pipeline, end to end.",
        "scope": CAPTION,
        "model": "rail",
        "units": [
            _unit("VAD"), _unit("Whisper"), _unit("LLM"), _unit("TTS"),
            _unit("Twilio-ready", "gate", signal=True),
            _unit("Arabic + English", "note"),
        ],
    },
}


def artefact_pair(slug: str) -> tuple[str, str]:
    """Return the landscape + vertical-rail SVG pair for one project page."""
    meta = ARTEFACT_META[slug]
    uid = f"dg-{re.sub(r'[^a-z0-9-]', '-', slug)}"
    model = meta.get("model", "rail")
    if model == "rail":
        wide, tall = rail(meta["units"], uid, meta["title"], meta["desc"])
    elif model == "trace":
        wide, tall = trace(meta["stages"], uid, meta["title"], meta["desc"],
                           crosscut=meta.get("crosscut"), boundary=meta.get("boundary"),
                           notes=meta.get("notes"), lane=meta.get("lane"))
    elif model == "contract":
        wide, tall = contract(uid, meta["title"], meta["desc"], head=meta["head"],
                              rows=meta["rows"], notes=meta["notes"])
    elif model == "hub":
        wide, tall = hub(meta["centre"], meta["band"], meta["band_notes"], meta["bus"],
                         meta["bus_side"], meta["lane"], uid, meta["title"], meta["desc"])
    elif model == "surfaces":
        wide, tall = surfaces(meta["items"], uid, meta["title"], meta["desc"])
    else:  # pragma: no cover - defensive
        raise SystemExit(f"unknown artefact model {model!r} for {slug}")
    return wide, tall


def system_map_pair(projects: dict[str, str]) -> tuple[str, str]:
    meta = ARTEFACT_META["system-map"]
    return system_map(projects, "dg-system-map", meta["title"], meta["desc"])
