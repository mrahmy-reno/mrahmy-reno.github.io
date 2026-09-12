#!/usr/bin/env python3
"""Static site generator for the Benchmark #1 portfolio.

No third-party dependencies (stdlib only). Renders the whole publish root (`docs/`) from:
  * `site.config.json`  - the single place the three owner-decision switches live
  * `tools/site_content.py` - every string, each tagged with its FACTS_LEDGER row

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
import site_content as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "site.config.json"

SITE_NAME_FALLBACK = "Mohammed Tawfiq Rahmy"
PAGES_INDEX = "index.html"


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

    return cfg


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
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<link rel="canonical" href="{esc(canonical)}">',
        f'<meta name="theme-color" content="#0d1b2a">',
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


def nav_hrefs(is_index: bool) -> dict:
    if is_index:
        return {
            "about": "#about", "experience": "#experience", "work": "#projects",
            "skills": "#skills", "education": "#education", "contact": "#contact",
        }
    return {
        "about": "/index.html#about", "experience": "/index.html#experience",
        "work": "/index.html#projects", "skills": "/index.html#skills",
        "education": "/index.html#education", "contact": "/index.html#contact",
    }


def render_header(cfg: dict, p: Page, is_index: bool) -> str:
    hrefs = nav_hrefs(is_index)
    nav = [
        ("nav_about", hrefs["about"]), ("nav_experience", hrefs["experience"]),
        ("nav_work", hrefs["work"]), ("nav_skills", hrefs["skills"]),
        ("nav_education", hrefs["education"]), ("nav_contact", hrefs["contact"]),
    ]
    items = "\n".join(
        f'            <li><a href="{href}">{p.t(C.L[key])}</a></li>' for key, href in nav
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
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" hidden>{p.t(C.L["menu"], global_=True)}</button>
      <nav class="site-nav" aria-label="Primary">
        <ul class="nav-list" id="primary-nav">
{items}
        </ul>
      </nav>
      <a class="btn btn-small header-contact" href="{C.LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">{p.t(C.L["header_contact"], global_=True)}<span class="visually-hidden"> {p.t(C.L["newtab"], global_=True)}</span></a>
    </div>
  </header>"""


def render_footer(cfg: dict, p: Page, is_index: bool) -> str:
    back = ('<p class="to-top"><a href="#top">'
            + p.t(C.L["back_to_top"], global_=True) + "</a></p>") if is_index else ""
    allwork = "" if is_index else (
        '<p class="to-top"><a href="/index.html#projects">'
        + p.t(C.L["all_work"], global_=True) + "</a></p>")
    return f"""  <footer class="site-footer">
    <div class="wrap footer-inner">
      <p class="footer-line"><span>{p.t(C.NAME, global_=True)}</span> · <a href="{C.LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">{p.t(C.L["header_contact"], global_=True)}<span class="visually-hidden"> {p.t(C.L["newtab"], global_=True)}</span></a> · <span>{p.t(C.L["footer_provenance"], global_=True)}</span></p>
      <p class="footer-line muted">{p.t(C.L["copyright"], global_=True)}</p>
{allwork}{back}
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


def render_facts_list(p: Page) -> str:
    rows = [
        (C.L["fact_current"], f'<strong>{p.t(C.CURRENT_ROLE)}</strong> · {p.t(C.CURRENT_EMPLOYER)} · {p.t(C.CURRENT_DATES)}'),
        (C.L["fact_based"], p.t(C.LOCATION)),
        (C.L["fact_focus"], p.t(C.FOCUS)),
        (C.L["fact_languages"], p.t(C.LANGUAGES)),
    ]
    out = []
    for label, value in rows:
        out.append(f'      <div class="fact"><dt>{p.t(label)}</dt><dd>{value}</dd></div>')
    return '<dl class="facts">\n' + "\n".join(out) + "\n    </dl>"


def render_photo(cfg: dict, p: Page) -> str:
    photo = cfg["photo"]
    if not photo.get("enabled"):
        return ""
    alt = C.b(photo["alt"], ["L1.1"], "verbatim",
              "Owner-approved likeness (ledger L1.5, Tier C released by the owner's decision). "
              "Alt text is the ledger name; self-hosted copy, never hot-linked.")
    p.rec.add(p.path, alt, True)
    return (f'      <img class="portrait" src="/{esc(photo["path"])}" alt="{esc(photo["alt"])}" '
            f'width="{int(photo["width"])}" height="{int(photo["height"])}" '
            f'decoding="async">')


# --------------------------------------------------------------------------- pages


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


def section_about(cfg: dict, p: Page) -> str:
    return f"""      <section class="section" id="about" aria-labelledby="about-h2">
        <div class="wrap">
          <h2 id="about-h2">{p.t(C.L["h2_about"])}</h2>
          <p class="lede">{p.t(C.S5_SUMMARY)}</p>
          <p>{p.t(C.ABOUT_SUMMARY)}</p>
{render_facts_list(p)}
        </div>
      </section>"""


def section_experience(cfg: dict, p: Page) -> str:
    blocks = []
    for i, role in enumerate(C.EXPERIENCE, start=1):
        bullets = "\n".join(f'              <li>{p.t(b)}</li>' for b in role["bullets"])
        blocks.append(f"""          <article class="exp" id="exp-{i}">
            <header class="exp-head">
              <h3>{p.t(role["title"])}</h3>
              <p class="exp-meta"><span class="employer">{p.t(role["employer"])}</span> · <span class="dates">{p.t(role["dates"])}</span></p>
            </header>
            <ul class="bullets">
{bullets}
            </ul>
          </article>""")
    return f"""      <section class="section" id="experience" aria-labelledby="experience-h2">
        <div class="wrap">
          <h2 id="experience-h2">{p.t(C.L["h2_experience"])}</h2>
          <div class="exp-list">
{chr(10).join(blocks)}
          </div>
        </div>
      </section>"""


GROUP_LABELS = {1: "g1", 2: "g2", 3: "g3"}


def section_projects(cfg: dict, p: Page) -> str:
    groups = []
    for gid in (1, 2, 3):
        cards = []
        for proj in C.PROJECTS:
            if proj["group"] != gid:
                continue
            cls = "card card-featured" if proj["featured"] else "card"
            featured = (f'<span class="tag">{p.t(C.L["featured"])}</span>'
                        if proj["featured"] else "")
            cards.append(
                f'              <li class="{cls}">\n'
                f'                <h4><a href="/projects/{proj["slug"]}.html">{p.t(proj["name"])}</a></h4>\n'
                f'                <p>{p.t(proj["one_liner"])}</p>\n'
                f'                {featured}\n'
                f'              </li>'
            )
        groups.append(f"""          <div class="project-group">
            <h3>{p.t(C.L[GROUP_LABELS[gid]])}</h3>
            <ul class="cards">
{chr(10).join(cards)}
            </ul>
          </div>""")
    return f"""      <section class="section" id="projects" aria-labelledby="work-h2">
        <div class="wrap">
          <h2 id="work-h2">{p.t(C.L["h2_work"])}</h2>
          <p class="section-intro">{p.t(C.L["projects_intro"])}</p>
{chr(10).join(groups)}
        </div>
      </section>"""


def section_skills(cfg: dict, p: Page) -> str:
    groups = []
    for label, chips in C.SKILL_GROUPS:
        items = "\n".join(
            f'              <li>{p.t(C.b(chip, refs))}</li>' for chip, refs in chips
        )
        groups.append(f"""          <div class="skill-group">
            <h3>{p.t(C.b(label, [], "structural"))}</h3>
            <ul class="chips">
{items}
            </ul>
          </div>""")
    return f"""      <section class="section" id="skills" aria-labelledby="skills-h2">
        <div class="wrap">
          <h2 id="skills-h2">{p.t(C.L["h2_skills"])}</h2>
          <div class="skill-list">
{chr(10).join(groups)}
          </div>
        </div>
      </section>"""


def section_education(cfg: dict, p: Page) -> str:
    edu = []
    for entry in C.EDUCATION:
        edu.append(f"""          <article class="edu">
            <h3>{p.t(entry["credential"])}</h3>
            <p class="edu-meta"><span>{p.t(entry["institution"])}</span> · <span>{p.t(entry["detail"])}</span> · <span class="year">{p.t(entry["year"])}</span></p>
          </article>""")
    certs = []
    for name, body, date in C.CERTIFICATIONS:
        date_html = (
            f' <span class="cert-date">{p.t(date)}</span>' if date is not None else ""
        )
        certs.append(
            f'              <li><span class="cert-name">{p.t(name)}</span> — '
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
          <h2 id="education-h2">{p.t(C.L["h2_education"])}</h2>
          <div class="edu-list">
{chr(10).join(edu)}
          </div>
          <h3 class="certs-h3">{p.t(C.L["h2_certs"])}</h3>
          <ul class="certs">
{chr(10).join(certs)}
          </ul>
{extra}
        </div>
      </section>"""


def section_contact(cfg: dict, p: Page) -> str:
    return f"""      <section class="section" id="contact" aria-labelledby="contact-h2">
        <div class="wrap">
          <h2 id="contact-h2">{p.t(C.L["h2_contact"])}</h2>
{render_contact_block(cfg, p)}
        </div>
      </section>"""


def build_index(cfg: dict, p: Page) -> str:
    title_block = C.b("Mohammed Tawfiq Rahmy — AI Solutions Engineer", ["L1.1", "L3.1"], "composed",
                      "Title composed from the ledger name (L1.1) and role (L3.1).")
    jsonld = render_jsonld(cfg)
    photo = render_photo(cfg, p)
    hero_media = f"""        <div class="hero-media">
{photo}
        </div>""" if photo else ""
    body = f"""      <section class="hero" id="top" aria-labelledby="hero-h1">
        <div class="wrap hero-inner">
          <div class="hero-text">
            <h1 id="hero-h1">{p.t(C.NAME)}</h1>
            <p class="eyebrow">{p.t(C.HEADLINE)}</p>
            <p class="pitch">{p.t(C.PITCH)}</p>
{render_facts_list(p)}
            <p class="cta-row"><a class="btn" href="#projects">{p.t(C.L["cta_work"])}</a> <a class="btn btn-ghost" href="{C.LINKEDIN_URL}" target="_blank" rel="noopener noreferrer">{p.t(C.L["cta_linkedin"])}<span class="visually-hidden"> {p.t(C.L["newtab"], global_=True)}</span></a></p>
          </div>
{hero_media}
        </div>
      </section>
{section_about(cfg, p)}
{section_experience(cfg, p)}
{section_projects(cfg, p)}
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


def build_project(cfg: dict, p: Page, proj: dict, idx: int) -> str:
    title_block = C.b(f'{proj["name"]["text"]} — Mohammed Tawfiq Rahmy', ["L1.1"],
                      "composed", "Title = the ledger project name plus the ledger name.")
    desc_block = C.b(proj["one_liner"]["text"], [proj["name"]["refs"][0]], "verbatim",
                     "Meta description = the ledger one-liner for this project.")
    overview = "\n".join(
        f'          <p>{p.t(par)}</p>' for par in proj["overview"]
    )
    caps = "\n".join(f'            <li>{p.t(cap)}</li>' for cap in proj["capabilities"])
    tech = ""
    if proj["tech_line"]:
        chips = "\n".join(f'              <li>{p.t(t)}</li>' for t in proj["tech_line"])
        tech = f"""          <div class="tech-row">
            <h3>{p.t(C.L["tech_line_label"])}</h3>
            <ul class="chips">
{chips}
            </ul>
          </div>"""
    prev_slug = C.PROJECT_ORDER[idx - 1] if idx > 0 else None
    next_slug = C.PROJECT_ORDER[idx + 1] if idx < len(C.PROJECT_ORDER) - 1 else None
    prev_html = ""
    if prev_slug:
        prev_proj = next(x for x in C.PROJECTS if x["slug"] == prev_slug)
        prev_html = (f'          <a class="pn-link pn-prev" href="/projects/{prev_slug}.html">'
                     f'<span class="pn-label">{p.t(C.L["prev"])}</span>'
                     f'<span class="pn-name">{p.t(prev_proj["name"])}</span></a>')
    next_html = ""
    if next_slug:
        next_proj = next(x for x in C.PROJECTS if x["slug"] == next_slug)
        next_html = (f'          <a class="pn-link pn-next" href="/projects/{next_slug}.html">'
                     f'<span class="pn-label">{p.t(C.L["next"])}</span>'
                     f'<span class="pn-name">{p.t(next_proj["name"])}</span></a>')
    body = f"""      <article class="section project-detail">
        <div class="wrap">
          <p class="breadcrumb"><a href="/index.html#projects">{p.t(C.L["all_work"])}</a></p>
          <h1>{p.t(proj["name"])}</h1>
          <p class="lede">{p.t(proj["one_liner"])}</p>
          <section class="proj-section" id="overview" aria-labelledby="overview-h2">
            <h2 id="overview-h2">{p.t(C.L["overview"])}</h2>
{overview}
          </section>
          <section class="proj-section" id="capabilities" aria-labelledby="capabilities-h2">
            <h2 id="capabilities-h2">{p.t(C.L["capabilities"])}</h2>
            <ul class="bullets">
{caps}
            </ul>
          </section>
{tech}
          <p class="scope-note">{p.t(C.SCOPE_NOTE)}</p>
          <nav class="prev-next" aria-label="Project navigation">
{prev_html}
{next_html}
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
    body = f"""      <section class="section notfound">
        <div class="wrap">
          <h1>{p.t(C.L["nf_h1"])}</h1>
          <p>{p.t(C.L["nf_body"])}</p>
          <p><a class="btn" href="/index.html">{p.t(C.L["nf_link"])}</a></p>
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
            '  <rect width="64" height="64" rx="12" fill="#0d1b2a"/>\n'
            '  <text x="32" y="42" font-family="Georgia, \'Times New Roman\', serif" '
            'font-size="30" font-weight="700" fill="#ffffff" text-anchor="middle">MR</text>\n'
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
              f"tier_b={len(cfg['certifications'].get('tier_b') or [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
