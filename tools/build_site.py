#!/usr/bin/env python3
"""Static site generator for the Benchmark #1 portfolio — B2-02 redesign.

No third-party dependencies (stdlib only). Renders the whole publish root (`docs/`) from:
  * `site.config.json`        - the single place the owner-decision switches live
  * `tools/site_content.py`   - every string, each tagged with its FACTS_LEDGER row
  * `tools/site_content_b2.py`- the redesign's additions (claim, point of view, glance labels, …)
  * `tools/artefacts.py`      - the original schematic SVG artefacts (PROOF_PLAN.md)

Usage:
    python3 tools/build_site.py                     # render into ./docs
    python3 tools/build_site.py --out /tmp/x        # render elsewhere (used by tests)
    python3 tools/build_site.py --config /tmp/c.json
"""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artefacts as A  # noqa: E402
import site_content as C  # noqa: E402
import site_content_b2 as C2  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "site.config.json"

SITE_NAME_FALLBACK = "Mohammed Tawfiq Rahmy"
PAGES_INDEX = "index.html"

THEME_COLOR = "#0c0e13"

GROUP_LABELS = {1: "g1", 2: "g2", 3: "g3"}


# --------------------------------------------------------------------------- utils


def esc(text: str) -> str:
    return html.escape(text, quote=True)


class Page:
    """A page being rendered: collects provenance blocks and produces HTML."""

    def __init__(self, recorder: "Recorder", path: str):
        self.rec = recorder
        self.path = path

    def t(self, block: dict, *, global_: bool = False) -> str:
        """Record a content block and return its HTML-escaped text."""
        self.rec.add(self.path, block, global_)
        return esc(block["text"])

    def raw(self, text: str, refs: list[str], mode: str, note: str, *, global_: bool = False) -> str:
        """Record an ad-hoc block (used for artefact captions owned by tools/artefacts.py)."""
        return self.t(C.b(text, refs, mode, note), global_=global_)


class Recorder:
    def __init__(self) -> None:
        self.entries: list[tuple[str, dict, bool]] = []

    def add(self, page: str, block: dict, global_: bool = False) -> None:
        self.entries.append((page, dict(block), global_))


# --------------------------------------------------------------------------- config


def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)

    def fail(msg: str) -> None:
        raise SystemExit(f"site.config.json is invalid: {msg}")

    if not isinstance(cfg.get("site"), dict):
        fail("missing 'site' object")
    if not cfg["site"].get("base_url"):
        fail("missing site.base_url")
    if not cfg["site"].get("lang"):
        cfg["site"]["lang"] = "en"
    if not cfg["site"].get("name"):
        cfg["site"]["name"] = SITE_NAME_FALLBACK

    contact = cfg.setdefault("contact", {})
    strategy = contact.get("strategy", "linkedin")
    if strategy not in ("linkedin", "email", "email_phone"):
        fail(f"contact.strategy must be linkedin|email|email_phone, got {strategy!r}")
    if strategy in ("email", "email_phone") and not contact.get("email"):
        fail(f"contact.strategy={strategy!r} requires contact.email (the exact FACTS_LEDGER "
             "section 8 value)")
    if strategy == "email_phone" and not contact.get("phone"):
        fail("contact.strategy='email_phone' requires contact.phone (the exact FACTS_LEDGER "
             "section 8 value)")

    photo = cfg.setdefault("photo", {})
    if photo.get("enabled"):
        if not photo.get("path"):
            fail("photo.enabled=true requires photo.path (a self-hosted file under docs/assets/)")
        if not photo.get("alt"):
            fail("photo.enabled=true requires photo.alt (factual alt text naming the owner)")
        photo.setdefault("width", 400)
        photo.setdefault("height", 400)

    certs = cfg.setdefault("certifications", {})
    if not isinstance(certs.get("tier_b", []), list):
        fail("certifications.tier_b must be a list")

    provenance = cfg.setdefault("provenance", {})
    tags = provenance.get("tags", "tier")
    if tags not in ("tier", "plain", "off"):
        fail(f"provenance.tags must be tier|plain|off, got {tags!r}")
    provenance["tags"] = tags

    return cfg


def source_tags(cfg: dict) -> str:
    return cfg["provenance"]["tags"]


# --------------------------------------------------------------------------- fragments


def render_head(cfg: dict, p: Page, *, title_block: dict, desc_block: dict,
                path: str, og_type: str, jsonld: str | None = None,
                noindex: bool = False) -> str:
    base = cfg["site"]["base_url"].rstrip("/") + "/"
    title = title_block["text"]
    desc = desc_block["text"]
    canonical = base + path
    p.rec.add(p.path, title_block)
    p.rec.add(p.path, desc_block)
    og_image = base + "assets/og-image.png"
    nm = C.NAME["text"]
    out = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        # Runs during head parsing, before the first layout pass: the enhancement class is set
        # without a post-load style recalculation, and the mobile nav control is only rendered
        # (by CSS) when JS is available, so the deferred script never mutates layout.
        '<script>document.documentElement.className='
        'document.documentElement.className.replace("no-js","js");</script>',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<link rel="canonical" href="{esc(canonical)}">',
        f'<meta name="theme-color" content="{THEME_COLOR}">',
    ]
    if noindex:
        out.append('<meta name="robots" content="noindex">')
    out += [
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{esc(nm)}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{esc(canonical)}">',
        f'<meta property="og:image" content="{esc(og_image)}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(nm)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{esc(og_image)}">',
        '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">',
        '<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">',
        '<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">',
        '<link rel="stylesheet" href="/assets/styles.css">',
        '<script src="/assets/main.js" defer></script>',
    ]
    if jsonld:
        out.append(jsonld)
    return "\n".join("    " + line for line in out)


def nav_hrefs(is_index: bool) -> list[tuple[str, str, str]]:
    """(content-key, href, section id for aria-current)."""
    items = [("nav_about", "about", "about"), ("nav_experience", "experience", "experience"),
             ("nav_work", "projects", "projects"), ("nav_skills", "skills", "skills"),
             ("nav_education", "education", "education"), ("nav_contact", "contact", "contact")]
    out = []
    for key, frag, sid in items:
        href = f"#{frag}" if is_index else f"/index.html#{frag}"
        out.append((key, href, sid))
    return out


def render_header(cfg: dict, p: Page, is_index: bool) -> str:
    items = "\n".join(
        f'            <li><a href="{href}" data-nav-section="{sid}">{p.t(C.L[key])}</a></li>'
        for key, href, sid in nav_hrefs(is_index)
    )
    # Print-only header line (A17). The index carries the role + employer (A17 asks for
    # name, current role + employer and the LinkedIn URL on the first printed page). Detail
    # pages deliberately carry only name + URL, so an employer name never appears on a page
    # that describes a project (attribution guard D17 / PRD 4.0.4).
    if is_index:
        print_text = (f'{C.NAME["text"]} — {C.CURRENT_ROLE["text"]}, '
                      f'{C.CURRENT_EMPLOYER["text"]} · {C.LINKEDIN_URL}')
        print_refs = ["L1.1", "S5-R2", "S5-R1", "L8.3"]
        print_note = ("Print-only header line assembled from mapped blocks (A17: name, current "
                      "role + employer and the LinkedIn URL readable on the first printed "
                      "page).")
    else:
        print_text = f'{C.NAME["text"]} · {C.LINKEDIN_URL}'
        print_refs = ["L1.1", "L8.3"]
        print_note = ("Print-only header line on a non-index page: name + LinkedIn URL only, so "
                      "no employer name appears next to a project description (D17). Uses the "
                      "same mapped blocks as the index variant.")
    print_contact = C.b(print_text, print_refs, "print", print_note)
    return f"""  <a class="skip-link" href="#main">{p.t(C.L["skip"], global_=True)}</a>
  <p class="print-only print-contact">{p.t(print_contact, global_=True)}</p>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="wordmark" href="/index.html">{p.t(C.NAME, global_=True)}</a>
      <span class="nav-slot"><button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav">{p.t(C.L["menu"], global_=True)}</button></span>
      <nav class="site-nav" aria-label="Primary">
        <ul class="nav-list" id="primary-nav">
{items}
        </ul>
      </nav>
      <a class="btn btn-small header-contact" href="{C.LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">{p.t(C.L["header_contact"], global_=True)}<span class="visually-hidden"> {p.t(C.L["newtab"], global_=True)}</span></a>
    </div>
  </header>"""


def render_footer(cfg: dict, p: Page, is_index: bool) -> str:
    legend = "\n".join(
        f'          <dd>{p.t(C2.EXTRA[key], global_=True)}</dd>'
        for key in ("legend_s1", "legend_s2", "legend_s3", "legend_s5")
    )
    allwork = "" if is_index else (
        f'      <p class="to-top"><a href="/index.html#projects">'
        + p.t(C.L["all_work"], global_=True) + "</a></p>")
    back = ('      <p class="to-top"><a href="#top">'
            + p.t(C.L["back_to_top"], global_=True) + "</a></p>") if is_index else ""
    return f"""  <footer class="site-footer">
    <div class="wrap">
      <p class="footer-line"><span>{p.t(C.NAME, global_=True)}</span> · <a href="{C.LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">{p.t(C.L["header_contact"], global_=True)}<span class="visually-hidden"> {p.t(C.L["newtab"], global_=True)}</span></a> · <span>{p.t(C.L["footer_provenance"], global_=True)}</span></p>
      <p class="footer-line muted">{p.t(C.L["copyright"], global_=True)}</p>
      <dl class="legend">
        <div>
          <dt>{p.t(C2.EXTRA["legend_h"], global_=True)}</dt>
{legend}
        </div>
      </dl>
{allwork}
{back}
    </div>
  </footer>"""


def render_contact_block(cfg: dict, p: Page) -> str:
    """The only place contact values may render (owner-decision switch surface)."""
    contact = cfg["contact"]
    strategy = contact["strategy"]
    rows = [
        f'      <p class="contact-cta"><a href="{C.LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">{p.t(C.L["contact_linkedin_text"])}<span class="visually-hidden"> {p.t(C.L["newtab"], global_=True)}</span></a></p>',
        f'      <p class="contact-url-url">{p.t(C.LINKEDIN_SHORT)}</p>',
    ]
    if strategy == "linkedin":
        rows.append(f'      <p class="contact-note">{p.t(C.L["contact_default_note"])}</p>')
    if strategy in ("email", "email_phone"):
        email_block = C.b(contact["email"], ["L8.1"], "verbatim",
                          "Owner-approved contact disclosure (FACTS_LEDGER 8.1, Tier A only "
                          "after the owner's decision). Renders only in the contact block.")
        rows.append(f'      <p class="contact-line"><span class="contact-label">Email</span> '
                    f'<span class="contact-value">{p.t(email_block)}</span></p>')
    if strategy == "email_phone":
        phone_block = C.b(contact["phone"], ["L8.2"], "verbatim",
                          "Owner-approved contact disclosure (FACTS_LEDGER 8.2, Tier A only "
                          "after the owner's decision). Renders only in the contact block.")
        rows.append(f'      <p class="contact-line"><span class="contact-label">Phone</span> '
                    f'<span class="contact-value">{p.t(phone_block)}</span></p>')
    return "\n".join(rows)


def render_photo(cfg: dict, p: Page) -> str:
    photo = cfg["photo"]
    if not photo.get("enabled"):
        return ""
    alt = C.b(photo["alt"], ["L1.1"], "verbatim",
              "Owner-approved likeness (ledger L1.5, Tier C released by the owner's decision). "
              "Alt text is the ledger name; self-hosted copy, never hot-linked.")
    p.rec.add(p.path, alt, True)
    return f"""        <div class="hero-media">
          <img class="portrait" src="/{esc(photo["path"])}" alt="{esc(photo["alt"])}" width="{int(photo["width"])}" height="{int(photo["height"])}" decoding="async">
        </div>"""


# --------------------------------------------------------------------------- motif


def attribution(p: Page, tags: str, tier: str = "S2") -> str:
    """The attribution rule: a hairline with a mono source tag seated on it (DESIGN_SYSTEM 6.10)."""
    if tags == "off":
        return '          <p class="attr-rule" aria-hidden="true"></p>'
    if tags == "plain":
        return (f'          <p class="attr-rule"><span class="srctag">'
                f'{p.t(C2.EXTRA["src_sourced"])}</span></p>')
    tag_block = C2.SOURCE_TAGS[tier]
    expansion = p.t(tag_block)
    return (f'          <p class="attr-rule"><span class="srctag" title="{esc(tag_block["text"].lstrip("— "))}">'
            f'<abbr>{esc(tier)}</abbr><span class="visually-hidden"> {expansion}</span></span></p>')


def section_head(p: Page, serial: dict, h2: dict, deck: dict, anchor: str) -> str:
    return f"""        <div class="section-head" data-reveal>
          <p class="serial">{p.t(serial)}</p>
          <h2 id="{anchor}-h2">{p.t(h2)}</h2>
          <p class="deck">{p.t(deck)}</p>
        </div>"""


def render_glance_strip(cfg: dict, p: Page) -> str:
    rows = [
        ("role", C2.ROLE_LEDGER),
        ("employer", C.CURRENT_EMPLOYER),
        ("since", C.CURRENT_DATES),
        ("based", C.LOCATION),
        ("focus", C.FOCUS),
        ("languages", C.LANGUAGES),
    ]
    out = []
    for key, value in rows:
        out.append(f'          <div class="glance-item"><dt>{p.t(C2.GLANCE[key])}</dt>'
                   f'<dd>{p.t(value)}</dd></div>')
    return '<dl class="glance-strip">\n' + "\n".join(out) + "\n        </dl>"


def render_figure(p: Page, uid: str, slug: str, *, refs: list[str] | None = None) -> str:
    """Render one artefact as figure(wide + tall SVG) with its caption and scope caption."""
    meta = A.ARTEFACT_META[slug]
    refs = refs or ["L4.1"]
    caption = p.raw(meta["caption"], refs, "composed",
                    "Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram "
                    "draws; asserts nothing beyond the project's ledger row.")
    scope = p.raw(meta["scope"], [], "structural",
                  "Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). "
                  "A statement about the drawing, not about the person.")
    wide, tall = A.artefact_pair(slug)
    return (f'        <figure class="artefact">\n'
            f'          <div class="artefact-frame">\n'
            + "\n".join("            " + line for line in wide.splitlines()) + "\n"
            + "\n".join("            " + line for line in tall.splitlines()) + "\n"
            f'          </div>\n'
            f'          <figcaption>{caption} <span class="scope-caption">{scope}</span></figcaption>\n'
            f'        </figure>')


def render_system_map(p: Page) -> str:
    meta = A.ARTEFACT_META["system-map"]
    wide, tall = A.system_map_pair({pr["slug"]: pr["name"]["text"] for pr in C.PROJECTS})
    caption = p.raw(meta["caption"], ["L4.1", "L4.2", "L4.3", "L4.4", "L4.5", "L4.6", "L4.7",
                                      "L4.8", "L4.9", "L4.10"], "composed",
                    "Structural caption for the system map. The ten node labels are the ledger "
                    "project names; the three group labels are the structural grouping.")
    scope = p.raw(meta["scope"], [], "structural",
                  "Mandatory scope caption (PROOF_PLAN.md section 5 rule 9).")
    link = f'<a href="#evidence">{p.t(C2.EXTRA["map_link"])}</a>'
    return (f'      <figure class="system-map" data-reveal>\n'
            + "\n".join("        " + line for line in wide.splitlines()) + "\n"
            + "\n".join("        " + line for line in tall.splitlines()) + "\n"
            f'        <figcaption>{caption} {link} → <span class="scope-caption">{scope}</span></figcaption>\n'
            f'      </figure>')


# --------------------------------------------------------------------------- index


def section_about(cfg: dict, p: Page) -> str:
    tags = source_tags(cfg)
    pov = C2.POINT_OF_VIEW
    pov_html = p.raw(pov["text"], pov["refs"], "composed", pov["note"])
    return f"""      <section class="section" id="about" aria-labelledby="about-h2">
        <div class="wrap">
{section_head(p, C2.SERIALS["about"], C.L["h2_about"], C2.EXTRA["about_deck"], "about")}
        <div class="prose" data-reveal>
          <p>{p.t(C.S5_SUMMARY)}</p>
          <p>{p.t(C.ABOUT_SUMMARY)}</p>
        </div>
        <p class="band-statement">{pov_html}</p>
{attribution(p, tags, "S5")}
        </div>
      </section>"""


def section_experience(cfg: dict, p: Page) -> str:
    blocks = []
    for i, role in enumerate(C.EXPERIENCE, start=1):
        bullets = "\n".join(f'              <li>{p.t(b)}</li>' for b in role["bullets"])
        current = "true" if i == 1 else "false"
        present = (f' <span class="present">{p.t(C2.EXTRA["present"])}</span>'
                   if i == 1 else "")
        blocks.append(f"""          <article class="exp" id="exp-{i}">
            <div class="exp-rail" data-current="{current}">
              <h3>{p.t(role["title"])}</h3>
              <p class="exp-meta"><span class="employer">{p.t(role["employer"])}</span> · <span class="dates">{p.t(role["dates"])}</span>{present}</p>
            </div>
            <ul class="bullets">
{bullets}
            </ul>
          </article>""")
    return f"""      <section class="section" id="experience" aria-labelledby="experience-h2">
        <div class="wrap">
{section_head(p, C2.SERIALS["experience"], C.L["h2_experience"], C2.EXTRA["experience_deck"], "experience")}
          <div class="exp-list" data-reveal>
{chr(10).join(blocks)}
          </div>
{attribution(p, source_tags(cfg), "S5")}
        </div>
      </section>"""


def section_projects(cfg: dict, p: Page) -> str:
    tags = source_tags(cfg)
    groups = []
    index = 0
    for gid in (1, 2, 3):
        cards = []
        for proj in C.PROJECTS:
            if proj["group"] != gid:
                continue
            index += 1
            cls = "card card-featured" if proj["featured"] else "card"
            featured = (f'<span class="tag">{p.t(C.L["featured"])}</span>'
                        if proj["featured"] else "")
            cards.append(
                f'              <li class="{cls}">\n'
                f'                <a class="row-inner" href="/projects/{proj["slug"]}.html">\n'
                f'                  <div class="row-head"><span class="rank">{p.t(C2.RANKS[index])}</span><h4><span class="row-title">{p.t(proj["name"])}</span></h4></div>\n'
                f'                  <p class="row-one-liner">{p.t(proj["one_liner"])}</p>\n'
                f'                  <span class="row-foot">{featured}<span class="arrow">{p.t(C.L["row_open"])} →</span></span>\n'
                f'                </a>\n'
                f'              </li>'
            )
        groups.append(f"""          <div class="work-group" data-reveal>
            <h3 class="work-group-head">{p.t(C.L[GROUP_LABELS[gid]])}</h3>
            <ul class="cards">
{chr(10).join(cards)}
            </ul>
          </div>""")
    return f"""      <section class="section" id="projects" aria-labelledby="work-h2">
        <div class="wrap">
{section_head(p, C2.SERIALS["work"], C.L["h2_work"], C2.EXTRA["work_deck"], "work")}
{chr(10).join(groups)}
{attribution(p, tags, "S2")}
        </div>
      </section>"""


def section_evidence(cfg: dict, p: Page) -> str:
    tags = source_tags(cfg)
    if tags == "off":
        inner = (f'        <div class="empty" data-reveal>\n'
                 f'          <span class="empty-label">{p.t(C2.EXTRA["empty_label"])}</span>\n'
                 f'          <p>{p.t(C2.EXTRA["empty_body"])}</p>\n'
                 f'        </div>')
    else:
        featured = next(pr for pr in C.PROJECTS if pr["slug"] == "smartops-soc-app")
        others = ["milo-ai-employee", "pulsesec", "halalbot", "sama-soc-triage"]
        items = []
        for slug in others:
            proj = next(pr for pr in C.PROJECTS if pr["slug"] == slug)
            items.append(
                f'            <li><span class="index-label">{p.t(C2.EXTRA["artefact_label"])}</span>'
                f'<a href="/projects/{slug}.html">{p.t(proj["name"])}</a></li>')
        inner = (f'        <div class="evidence-figure" data-reveal>\n'
                 f'{render_figure(p, "dg-smartops", "smartops-soc-app", refs=featured["name"]["refs"])}\n'
                 f'        </div>\n'
                 f'        <h3 class="certs-h3">{p.t(C2.EXTRA["evidence_index_h"])}</h3>\n'
                 f'        <ul class="evidence-index">\n' + "\n".join(items) + "\n        </ul>")
    more = (f'        <p class="to-top"><a class="btn btn-secondary" href="#projects">'
            f'{p.t(C2.EXTRA["evidence_more"])}</a></p>')
    return f"""      <section class="band band-signal section" id="evidence" aria-labelledby="evidence-h2">
        <div class="wrap">
{section_head(p, C2.SERIALS["evidence"], C2.EXTRA["evidence_h2"], C2.EXTRA["evidence_deck"], "evidence")}
{inner}
{more}
{attribution(p, tags, "S2")}
        </div>
      </section>"""


def section_skills(cfg: dict, p: Page) -> str:
    groups = []
    for label, chips in C.SKILL_GROUPS:
        items = "\n".join(
            f'              <li>{p.t(C.b(chip, refs))}</li>' for chip, refs in chips
        )
        groups.append(f"""          <div class="skill-group" data-reveal>
            <h3>{p.t(C.b(label, [], "structural"))}</h3>
            <ul class="chips">
{items}
            </ul>
          </div>""")
    return f"""      <section class="section" id="skills" aria-labelledby="skills-h2">
        <div class="wrap">
{section_head(p, C2.SERIALS["skills"], C.L["h2_skills"], C2.EXTRA["skills_deck"], "skills")}
          <div class="skill-list">
{chr(10).join(groups)}
          </div>
{attribution(p, source_tags(cfg), "S5")}
        </div>
      </section>"""


def section_education(cfg: dict, p: Page) -> str:
    edu = []
    for entry in C.EDUCATION:
        edu.append(f"""          <article class="edu" data-reveal>
            <h3>{p.t(entry["credential"])}</h3>
            <p class="edu-meta"><span>{p.t(entry["institution"])}</span> · <span>{p.t(entry["detail"])}</span> · <span class="year">{p.t(entry["year"])}</span></p>
          </article>""")
    certs = []
    for name, body, date in C.CERTIFICATIONS:
        date_html = (
            f' <span class="cert-date">{p.t(date)}</span>' if date is not None else ""
        )
        certs.append(
            f'            <li><span class="cert-name">{p.t(name)}</span> — '
            f'<span class="cert-body">{p.t(body)}</span>{date_html}</li>'
        )
    extra = ""
    tier_b = cfg["certifications"].get("tier_b") or []
    if tier_b:
        rows = []
        for item in tier_b:
            name = item.get("name", "")
            body = item.get("body", "")
            blk = C.b(name, ["L7.6"], "verbatim",
                      "Tier-B certification activated by the owner via site.config.json; the "
                      "ledger row must exist before the switch is flipped (A16).")
            blk2 = C.b(body, ["L7.6"], "verbatim", "Tier-B issuing body / details.")
            rows.append(f'              <li><span class="cert-name">{p.t(blk)}</span> — '
                        f'<span class="cert-body">{p.t(blk2)}</span></li>')
        extra = ('          <h3 class="certs-h3-tierb">Additional certifications</h3>\n'
                 '          <ul class="certs">\n' + "\n".join(rows) + "\n          </ul>")
    return f"""      <section class="section" id="education" aria-labelledby="education-h2">
        <div class="wrap">
{section_head(p, C2.SERIALS["education"], C.L["h2_education"], C2.EXTRA["education_deck"], "education")}
          <div class="edu-list">
{chr(10).join(edu)}
          </div>
          <h3 class="certs-h3">{p.t(C.L["h2_certs"])}</h3>
          <ul class="certs">
{chr(10).join(certs)}
          </ul>
{extra}
{attribution(p, source_tags(cfg), "S5")}
        </div>
      </section>"""


def section_contact(cfg: dict, p: Page) -> str:
    return f"""      <section class="section" id="contact" aria-labelledby="contact-h2">
        <div class="wrap">
{section_head(p, C2.SERIALS["contact"], C.L["h2_contact"], C2.EXTRA["contact_deck"], "contact")}
          <div class="contact-panel" data-reveal>
{render_contact_block(cfg, p)}
          </div>
        </div>
      </section>"""


def build_index(cfg: dict, p: Page) -> str:
    title_block = C.b("Mohammed Tawfiq Rahmy — AI Solutions Engineer", ["L1.1", "L3.1"], "composed",
                      "Title composed from the ledger name (L1.1) and role (L3.1).")
    jsonld = render_jsonld(cfg)
    photo = render_photo(cfg, p)
    body = f"""      <section class="band band-trace hero" id="top" aria-labelledby="hero-h1">
        <div class="wrap hero-inner">
          <div class="hero-text" data-reveal="hero">
            <p class="eyebrow">{p.t(C.HEADLINE)}</p>
            <h1 id="hero-h1">{p.t(C.NAME)}</h1>
            <p class="claim">{p.t(C2.CLAIM_LEAD)} <span class="claim-tail">{p.t(C2.CLAIM_TAIL)}</span></p>
          </div>
          <div class="hero-aside" data-reveal>
{photo}
{render_glance_strip(cfg, p)}
          </div>
          <div class="hero-cta">
            <p class="cta-row"><a class="btn" href="#projects">{p.t(C.L["cta_work"])}</a> <a class="btn btn-secondary" href="{C.LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">{p.t(C.L["cta_linkedin"])}<span class="visually-hidden"> {p.t(C.L["newtab"], global_=True)}</span></a></p>
          </div>
          <div class="hero-pitch">
            <p class="pitch">{p.t(C.PITCH)}</p>
          </div>
        </div>
{render_system_map(p)}
      </section>
{section_about(cfg, p)}
{section_experience(cfg, p)}
{section_projects(cfg, p)}
{section_evidence(cfg, p)}
{section_skills(cfg, p)}
{section_education(cfg, p)}
{section_contact(cfg, p)}"""
    return page_shell(cfg, p, title_block=title_block, desc_block=C.META_DESCRIPTION,
                      path=PAGES_INDEX, body=body, og_type="profile", is_index=True,
                      jsonld=jsonld)


def render_jsonld(cfg: dict) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": C.NAME["text"],
        "jobTitle": C.CURRENT_ROLE["text"],
        "url": cfg["site"]["base_url"],
        "sameAs": [C.LINKEDIN_URL],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "New Cairo",
            "addressCountry": "Egypt",
        },
        "alumniOf": [
            {"@type": "EducationalOrganization", "name": e["institution"]["text"]}
            for e in C.EDUCATION
        ],
        "knowsLanguage": ["Arabic", "English", "German"],
        "hasCredential": [
            {
                "@type": "EducationalOccupationalCredential",
                "name": name["text"],
                "recognizedBy": {"@type": "Organization", "name": body["text"]},
            }
            for name, body, _date in C.CERTIFICATIONS
        ],
    }
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    indented = "\n".join("    " + line for line in payload.splitlines())
    return f'    <script type="application/ld+json">\n{indented}\n    </script>'


# --------------------------------------------------------------------------- case study


def page_shell(cfg: dict, p: Page, *, title_block: dict, desc_block: dict, path: str,
               body: str, og_type: str = "website", is_index: bool = False,
               jsonld: str | None = None, noindex: bool = False) -> str:
    lang = esc(cfg["site"]["lang"])
    return f"""<!DOCTYPE html>
<html lang="{lang}" class="no-js">
  <head>
{render_head(cfg, p, title_block=title_block, desc_block=desc_block, path=path,
             og_type=og_type, jsonld=jsonld, noindex=noindex)}
  </head>
  <body>
{render_header(cfg, p, is_index)}
    <main id="main">
{body}
    </main>
{render_footer(cfg, p, is_index)}
  </body>
</html>
"""


CASE_STAGE_KEYS = [
    (1, "cs-problem", "stage_problem", "problem"),
    (2, "cs-approach", "stage_approach", "approach"),
    (4, "cs-hard", "stage_hard", "hard"),
    (6, "cs-outcome", "stage_outcome", "outcome"),
]


def stage_block(p: Page, num: int, cls: str, label_key: str, text: str | None,
                refs: list[str]) -> str:
    label = p.t(C2.STAGE_SERIALS[num])
    head = (f'            <p class="cs-label">{label} · {p.t(C.L[label_key])}</p>')
    if text is None:
        empty = (f'            <div class="empty"><span class="empty-label">'
                 f'{p.t(C2.EXTRA["empty_label"])}</span>'
                 f'<p>{p.t(C2.EXTRA["empty_body"])}</p></div>')
        return (f'          <section class="cs-stage {cls}">\n'
                f'            <div class="cs-stage-inner">\n{head}\n{empty}\n'
                f'            </div>\n          </section>')
    note = ("Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / "
            "approved-extension phrases; connective verbs only.")
    para = p.raw(text, refs, "composed", note)
    return (f'          <section class="cs-stage {cls}">\n'
            f'            <div class="cs-stage-inner">\n{head}\n'
            f'            <div class="cs-body"><p>{para}</p></div>\n'
            f'            </div>\n          </section>')


def build_project(cfg: dict, p: Page, proj: dict, idx: int) -> str:
    tags = source_tags(cfg)
    title_block = C.b(f'{proj["name"]["text"]} — Mohammed Tawfiq Rahmy', ["L1.1"],
                      "composed", "Title = the ledger project name plus the ledger name.")
    desc_block = C.b(proj["one_liner"]["text"], [proj["name"]["refs"][0]], "verbatim",
                     "Meta description = the ledger one-liner for this project.")
    stages = C2.CASE_STAGES[proj["slug"]]
    overview = "\n".join(
        f'            <p>{p.t(par)}</p>' for par in proj["overview"]
    )
    caps = "\n".join(f'              <li>{p.t(cap)}</li>' for cap in proj["capabilities"])
    tech = ""
    if proj["tech_line"]:
        chips = "\n".join(f'                <li>{p.t(t)}</li>' for t in proj["tech_line"])
        tech = f"""          <div class="tech-row" data-reveal>
            <h3>{p.t(C.L["tech_line_label"])}</h3>
            <ul class="chips">
{chips}
            </ul>
          </div>"""
    problem = stage_block(p, 1, "cs-problem", "stage_problem", stages["problem"][0],
                          stages["problem"][1])
    approach = stage_block(p, 2, "cs-approach", "stage_approach", stages["approach"][0],
                           stages["approach"][1])
    hard = stage_block(p, 4, "cs-hard", "stage_hard",
                       stages["hard"][0] if stages["hard"] else None,
                       stages["hard"][1] if stages["hard"] else [])
    outcome = stage_block(p, 6, "cs-outcome", "stage_outcome", stages["outcome"][0],
                          stages["outcome"][1])
    artefact = render_figure(p, f"dg-{proj['slug']}", proj["slug"], refs=proj["name"]["refs"])
    domain = C.L[GROUP_LABELS[proj["group"]]]
    prev_slug = C.PROJECT_ORDER[idx - 1] if idx > 0 else None
    next_slug = C.PROJECT_ORDER[idx + 1] if idx < len(C.PROJECT_ORDER) - 1 else None
    pn = []
    for slug, key, cls in ((prev_slug, "prev", "pn-prev"), (next_slug, "next", "pn-next")):
        if not slug:
            continue
        other = next(x for x in C.PROJECTS if x["slug"] == slug)
        pn.append(f'          <a class="pn-link {cls}" href="/projects/{slug}.html">'
                  f'<span class="pn-label">{p.t(C.L[key])}</span>'
                  f'<span class="pn-name">{p.t(other["name"])}</span></a>')
    body = f"""      <article class="project-detail">
        <div class="wrap">
          <p class="breadcrumb"><a href="/index.html#projects">{p.t(C.L["all_work"])}</a></p>
          <h1 class="project-title">{p.t(proj["name"])}</h1>
          <p class="project-lede">{p.t(proj["one_liner"])}</p>
          <p class="project-meta"><span class="tag">{p.t(domain)}</span><span class="cs-label">{p.t(C2.STAGE_SERIALS[3])} · {p.t(C.L["stage_architecture"])}</span></p>
          <section class="cs-stage" id="overview" aria-labelledby="overview-h2">
            <div class="cs-stage-inner">
              <p class="cs-label">{p.t(C2.EXTRA["overview_label"])}</p>
              <div class="cs-body">
                <h2 id="overview-h2">{p.t(C2.EXTRA["overview_label"])}</h2>
{overview}
              </div>
            </div>
          </section>
{problem}
{approach}
          <section class="cs-stage cs-architecture" aria-labelledby="architecture-h2">
            <div class="wrap">
              <div class="cs-stage-inner">
                <p class="cs-label">{p.t(C2.STAGE_SERIALS[3])} · {p.t(C.L["stage_architecture"])}</p>
                <div class="cs-body">
                  <h2 id="architecture-h2">{p.t(C.L["stage_architecture"])}</h2>
                  <div class="diagram-panel" data-reveal>
{artefact}
                  </div>
                </div>
              </div>
            </div>
          </section>
{hard}
          <section class="cs-stage cs-evidence" aria-labelledby="evidence-h2">
            <div class="cs-stage-inner">
              <p class="cs-label">{p.t(C2.STAGE_SERIALS[5])} · {p.t(C.L["stage_evidence"])}</p>
              <div class="cs-body">
                <h2 id="evidence-h2">{p.t(C.L["stage_evidence"])}</h2>
                <div class="evidence-panel" data-reveal>
                  <h3>{p.t(C.L["capabilities"])}</h3>
                  <ul class="bullets">
{caps}
                  </ul>
                </div>
{tech}
                <p class="callout"><span class="callout-label">{p.t(C2.EXTRA["scope_label"])}</span>{p.t(C.SCOPE_NOTE)}</p>
              </div>
            </div>
          </section>
{outcome}
{attribution(p, tags, "S2")}
          <nav class="prev-next" aria-label="Project navigation">
{chr(10).join(pn)}
          </nav>
        </div>
      </article>"""
    return page_shell(cfg, p, title_block=title_block, desc_block=desc_block,
                      path=f'projects/{proj["slug"]}.html', body=body, og_type="article")


def build_404(cfg: dict, p: Page) -> str:
    title_block = C.b("Page not found — Mohammed Tawfiq Rahmy", ["L1.1"], "composed",
                      "Composed from the structural string 'Page not found' and the ledger name.")
    desc_block = C.b("The page you were looking for is not on this site.", [], "structural",
                     "Structural; asserts nothing about the person.")
    links = "\n".join(
        f'          <li><a href="/projects/{pr["slug"]}.html">{p.t(pr["name"])}</a></li>'
        for pr in C.PROJECTS
    )
    body = f"""      <section class="section notfound">
        <div class="wrap">
          <h1>{p.t(C2.EXTRA["nf_h1_v2"])}</h1>
          <p>{p.t(C2.EXTRA["nf_body_v2"])}</p>
          <p><a class="btn" href="/index.html">{p.t(C.L["nf_link"])}</a></p>
          <h2>{p.t(C2.EXTRA["all_projects"])}</h2>
          <ul class="evidence-index">
{links}
          </ul>
{render_contact_block(cfg, p)}
        </div>
      </section>"""
    return page_shell(cfg, p, title_block=title_block, desc_block=desc_block,
                      path="404.html", body=body, og_type="website", noindex=True)


# --------------------------------------------------------------------------- static files


def sitemap_xml(cfg: dict) -> str:
    base = cfg["site"]["base_url"].rstrip("/") + "/"
    paths = [PAGES_INDEX] + [f'projects/{s}.html' for s in C.PROJECT_ORDER]
    urls = "\n".join(f"  <url>\n    <loc>{base}{p}</loc>\n  </url>" for p in paths)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n")


def robots_txt(cfg: dict) -> str:
    base = cfg["site"]["base_url"].rstrip("/") + "/"
    return f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n"


def favicon_svg() -> str:
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" '
            'aria-label="Mohammed Tawfiq Rahmy">\n'
            '  <rect width="64" height="64" rx="12" fill="#0c0e13"/>\n'
            '  <rect x="1" y="1" width="62" height="62" rx="11" fill="none" stroke="#2a313d"/>\n'
            '  <rect x="12" y="50" width="40" height="2" fill="#58c9be"/>\n'
            '  <text x="32" y="44" font-family="Georgia, \'Times New Roman\', serif" '
            'font-size="30" font-weight="700" fill="#f2a93b" text-anchor="middle">MR</text>\n'
            '</svg>\n')


# --------------------------------------------------------------------------- driver


def render_all(cfg: dict, outdir: Path, recorder: Recorder | None = None) -> dict:
    rec = recorder if recorder is not None else Recorder()
    files: dict[str, str] = {}

    def write(rel: str, content: str) -> None:
        if rel.endswith((".html", ".svg", ".xml", ".css", ".js")):
            content = "\n".join(line.rstrip() for line in content.splitlines())
            if content and not content.endswith("\n"):
                content += "\n"
        files[rel] = content

    write(".nojekyll", "")
    write("robots.txt", robots_txt(cfg))
    write("sitemap.xml", sitemap_xml(cfg))
    write("assets/favicon.svg", favicon_svg())
    write(PAGES_INDEX, build_index(cfg, Page(rec, PAGES_INDEX)))
    write("404.html", build_404(cfg, Page(rec, "404.html")))
    for i, proj in enumerate(C.PROJECTS):
        rel = f'projects/{proj["slug"]}.html'
        write(rel, build_project(cfg, Page(rec, rel), proj, i))

    if outdir is not None:
        for rel, content in files.items():
            target = outdir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description="Render the portfolio site into docs/")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--out", default=str(ROOT / "docs"))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    files = render_all(cfg, outdir)
    if not args.quiet:
        print(f"rendered {len(files)} files into {outdir}")
        print(f"contact.strategy={cfg['contact']['strategy']} "
              f"photo.enabled={bool(cfg['photo'].get('enabled'))} "
              f"tier_b={len(cfg['certifications'].get('tier_b') or [])} "
              f"provenance.tags={cfg['provenance']['tags']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
