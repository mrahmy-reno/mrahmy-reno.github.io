"""Content model — B2-02 additions (the redesign's new strings).

Split out of `site_content.py` only to keep that file readable; every block here is declared the
same way and is imported back into it, so there is still exactly one place a rendered string can
come from. Nothing here introduces a fact: each block is either the ledger's own words, a
structural label, or a composition under R2 whose phrase list is in the note.

Ref ids are the FACTS_LEDGER.md row ids used by `site_content.py`; `@4.1` means the ledger's
section 4.1 approved-extension table.
"""

from __future__ import annotations

from site_content import b

# ---------------------------------------------------------------- the hero claim (R2)

CLAIM_LEAD = b(
    "I build production agentic systems:",
    ["L2.1", "L3.4"],
    "composed",
    "ART_DIRECTION.md section 2, composition rule R2. Phrases: 'I build' (verb, free under R2) + "
    "'production agentic systems' (L2.1, verbatim). No noun, technology, employer, date, client, "
    "metric or scope detail is added.",
)

CLAIM_TAIL = b(
    "grounded, evaluated, approval-bound.",
    ["L3.4", "L4.1", "L4.3"],
    "composed",
    "ART_DIRECTION.md section 2, R2. Phrases: 'grounding/evidence controls' and 'grounding "
    "controls' (L3.4 / L4.1) -> 'grounded'; 'evaluation-gated agent development' (L3.4) and "
    "'evaluation gates' (L4.1) -> 'evaluated'; 'approval binding' (L4.3) -> 'approval-bound'. The "
    "claim is a compression of phrases the ledger already prints, not a new assertion.",
)

# ---------------------------------------------------------------- the editorial point of view (Q9)

POINT_OF_VIEW = b(
    "Agentic systems are only useful if their answers can be checked: grounding/evidence "
    "controls, typed contracts, evaluation gates, approval binding, authority boundaries, "
    "evidence-linked findings, replayable traces, idempotent actions and reconciliation.",
    ["L4.1", "L4.2", "L4.3", "L3.4"],
    "composed",
    "PROOF_PLAN.md section 7's sanctioned construction, at the phrase level: the framing clause is "
    "PROOF_PLAN section 7's own sentence, and every substantive phrase after the colon is a ledger "
    "phrase ('grounding/evidence controls', 'typed contracts' L4.1; 'evidence-linked findings', "
    "'replayable traces' L4.2; 'approval binding', 'authority boundaries', 'idempotent actions "
    "and reconciliation' L4.3; 'evaluation gates' L4.1@4.1). No new noun, technology, employer, "
    "date, client or metric enters the sentence.",
)

# ---------------------------------------------------------------- at-a-glance strip

GLANCE = {
    "role": b("Current role", [], "structural"),
    "employer": b("Employer", [], "structural"),
    "since": b("Since", [], "structural"),
    "based": b("Based in", [], "structural"),
    "focus": b("Focus", [], "structural"),
    "languages": b("Languages", [], "structural"),
}

# The role, wherever it is asserted as a FIELD (at-a-glance strip, page <title>, JSON-LD,
# experience entry, print line). The formal title is FACTS_LEDGER.md §11 row R2 (source S5,
# which wins over the older "AI Solutions Engineer" of L3.1). The older variant survives only
# inside owner-authored summary prose (PITCH / S5_SUMMARY / ABOUT_SUMMARY / META_DESCRIPTION).
ROLE_LEDGER = b("Associate Solutions Engineer — AI / GenAI Solutions", ["S5-R2"], "verbatim",
                "The formal current role title (FACTS_LEDGER.md §11 R2, source S5). Used wherever "
                "a role is asserted as a field. The older L3.1 token 'AI Solutions Engineer' is "
                "retained only inside owner-authored summary prose.")

# ---------------------------------------------------------------- section decks & stage serials
#
# B2-04 / D4: the index's `NN / 07` section serials are gone (the critique named them as a
# report's page numbering applied to a portfolio), so there is no SERIALS table here any more.
# The CASE-STUDY stage serials stay: `01 / 06 · PROBLEM` is the six-stage shape Q5 asks for, and
# it is a device of the case study, not of the index.

STAGE_SERIALS = {
    1: b("01 / 06", [], "structural", "Case-study stage serial."),
    2: b("02 / 06", [], "structural", "Case-study stage serial."),
    3: b("03 / 06", [], "structural", "Case-study stage serial."),
    4: b("04 / 06", [], "structural", "Case-study stage serial."),
    5: b("05 / 06", [], "structural", "Case-study stage serial."),
    6: b("06 / 06", [], "structural", "Case-study stage serial."),
}

# The index rows carry a catalogue position (01-10) in ledger order. It is a position marker,
# not a ranking: nothing about quality or importance is asserted by it.
RANKS = {n: b(f"{n:02d}", [], "structural",
              "Project catalogue position, in the ledger's own L4.1-L4.10 order.")
         for n in range(1, 11)}

EXTRA = {
    "work_deck": b("Ten projects across security-operations agents, applied RAG and analytics, "
                   "and shipped products.", [], "structural",
                   "Structural deck: names the three groups that the rows themselves render."),
    "evidence_h2": b("Work, shown", [], "structural"),
    "evidence_deck": b("How one of them runs: the stages, the controls bound across them, and "
                       "the contract at the end.", [], "structural",
                       "Structural deck describing what the two objects below it draw. It no "
                       "longer claims a map of the series (B2-04 / D3: the section used to draw "
                       "the ten project names)."),
    "evidence_index_h": b("Also drawn", [], "structural"),
    "evidence_more": b("All ten projects", [], "structural"),
    "map_caption": b("Ten projects — how they fit together.", [], "structural"),
    "map_link": b("See one, drawn", [], "structural"),
    "about_deck": b("Why this work matters, in the terms the work itself uses.", [], "structural"),
    "pov_label": b("Point of view", [], "structural"),
    "experience_deck": b("Roles and dates, newest first.", [], "structural"),
    "skills_deck": b("The stack, grouped. Names are the ledger's own.", [], "structural"),
    "education_deck": b("Credentials and the bodies that issued them.", [], "structural"),
    "contact_deck": b("One route, and it is LinkedIn.", [], "structural"),
    "scope_label": b("Scope", [], "structural"),
    "overview_label": b("Overview", [], "structural"),
    "artefact_label": b("Artefact", [], "structural"),
    "src_human": b("Sources: the owner's own profile, résumé and project notes.", [], "structural",
                   "B2-04 / D5: the human-readable form of the attribution rule. It replaces the "
                   "visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, "
                   "which were QA vocabulary published to the visitor. The tier taxonomy still "
                   "governs the build and still reaches the DOM as data-source-tiers on the "
                   "attribution rule; it asserts nothing about the person."),
    "src_sourced": b("SOURCED", [], "structural"),
    "empty_label": b("NOT YET PUBLISHED", [], "structural"),
    "empty_body": b("This block is withheld until its source is published on this site.", [],
                    "structural",
                    "Process statement about this site's publication rule; asserts nothing about "
                    "the person."),
    "nf_h1_v2": b("This path isn't here.", [], "structural"),
    "nf_body_v2": b("The page you were looking for is not on this site.", [], "structural"),
    "nf_map": b("Every published page, mapped.", [], "structural"),
    "skip_to_work": b("Skip to the work", [], "structural"),
    "present": b("Present", [], "structural",
                 "Factual state marker on the current role (L3.1 dates)."),
    "all_projects": b("All ten projects", [], "structural"),
}

# B2-04 / D5: the SOURCE_TAGS table (the visually-hidden expansion of the S1/S2/S3/S5 tokens) is
# gone with the visible token itself. The tiers remain a build-level fact: `attribution()` writes
# them to the DOM as data-source-tiers, and the content map records the tier of every block.

# ---------------------------------------------------------------- SIGNAL / MTR: the signal

# The signal is one mark with one meaning, admitted only by C1 (active), C2 (verified),
# C3 (consequential) or C4 (attention-worthy), and it is always paired with a label in the
# instrument voice (DESIGN_LANGUAGE.md §3.6). These are the labels in use on this site, each with
# the condition it names. Most pages ship zero signals — that is the language's normal state
# (DNA §3.5), and it is demonstrated on nine of the twelve pages.
SIGNAL = {
    # C1 ACTIVE — true now, and not true at an earlier time. The current role and employer.
    "active": b("Active", [], "structural",
                "Signal label (DESIGN_LANGUAGE.md §3.6). Condition C1 ACTIVE: the current role "
                "is true now and was not true before. Label is a noun-of-state, not an "
                "encouragement (DNA §5.6)."),
    # C3 CONSEQUENTIAL — a scope boundary turns here. SAMA is client work (ledger §4 note:
    # 'mention depth, never internals'), so reading past the scope note has a cost if misread.
    "scope": b("Scope", [], "structural",
               "Signal label (DESIGN_LANGUAGE.md §3.6). Condition C3 CONSEQUENTIAL: a scope "
               "boundary the ledger itself imposes on this project row (FACTS_LEDGER §4, S3)."),
}

# ---------------------------------------------------------------- the expression system

# Every page declares its expression: a MODE (EXPRESSION_SYSTEM.md §2 — leading surface, scale
# band, signal budget, motion budget) and a layout ARCHETYPE (§4 — the arrangement of planes).
# The composition is chosen after the content, and no two consecutive pages in the series share
# an archetype (§4 rule 1). These are structural declarations, not claims.
#
#   mode   M1 editorial-quiet · M2 instrument-dense · M3 signal-forward · M4 archival
#   arch   A2 rail & content · A3 hub/broker · A4 stage-gate · A5 register · A6 plate ·
#          A8 marginalia
#
# `surface` is the LEADING surface (DNA §4.2/§4.3: one surface leads, ≥70% of planes).
# `close` names the one sanctioned transition when the page has one, with its reason (DNA §4.4):
#   T1 claim → proof · T2 human → system · T3 narrative → reference · T4 overview → detail
EXPRESSION: dict[str, dict] = {
    # A4 stage-gate · M2 instrument-dense · deep-led · zero transitions
    "sama-soc-triage": {"mode": "M2", "arch": "A4", "surface": "deep"},
    # A3 hub/broker · M2 instrument-dense · deep-led · zero transitions
    "smartops-soc-app": {"mode": "M2", "arch": "A3", "surface": "deep"},
    # A6 plate · M2 → M1 close · deep-led, T2 at the human close
    "milo-ai-employee": {"mode": "M2", "arch": "A6", "surface": "deep",
                         "close": ("warm", "T2")},
    # A5 register · M4 archival · warm-led · zero motion
    "pulsesec": {"mode": "M4", "arch": "A5", "surface": "warm"},
    # A4 stage-gate · M2 instrument-dense · deep-led
    "tonsy-gpt": {"mode": "M2", "arch": "A4", "surface": "deep"},
    # A3 hub/broker · M2 instrument-dense · deep-led
    "smart-care": {"mode": "M2", "arch": "A3", "surface": "deep"},
    # A8 marginalia · M1 editorial-quiet · warm-led
    "halalbot": {"mode": "M1", "arch": "A8", "surface": "warm"},
    # A6 plate · M2 → M1 close · deep-led, T2 at the human close
    "forwheelz": {"mode": "M2", "arch": "A6", "surface": "deep",
                  "close": ("warm", "T2")},
    # A5 register · M4 archival · warm-led
    "email-mcp": {"mode": "M4", "arch": "A5", "surface": "warm"},
    # A8 marginalia · M1 editorial-quiet · warm-led
    "voice-agent-core": {"mode": "M1", "arch": "A8", "surface": "warm"},
}

# The index's own expression (EXPRESSION_SYSTEM.md §3.2: site index → M1 leads, M2 passage,
# A2 rail & content, ≤1 signal on the lead, one transition into the artefact plate).
INDEX_EXPRESSION = {"mode": "M1", "arch": "A2", "surface": "warm",
                    "close": ("deep", "T1")}

# Plane headings the archetypes introduce. Structural: they name the arrangement, not the work.
ARCH = {
    "rail": b("Register", [], "structural",
              "Archetype label for the rail column (A2 rail & content). Names the column, "
              "asserts nothing."),
    "hub": b("The system", [], "structural",
             "Archetype label for the hub plane (A3 hub/broker). Names the centre of the "
             "drawing."),
    "spokes": b("The parts", [], "structural",
                "Archetype label for the bounded spokes around the hub."),
    "gate": b("Decision gate", [], "structural",
              "Archetype label for the gate between two stages (A4 stage-gate)."),
    "plate": b("The drawing", [], "structural",
               "Archetype label for the plate (A6 plate)."),
    "margin": b("Notes", [], "structural",
                "Archetype label for the margin column (A8 marginalia)."),
    "close": b("What it is", [], "structural",
               "Archetype label for the closing human plane (the T2 close)."),
}

# ---------------------------------------------------------------- case-study stage copy

# Stage copy is deliberately short. Every substantive phrase is taken from the project's own
# ledger row / approved-extension row; the connective verbs are the only free words, exactly as
# PRD 3.4 permits. A project whose approved pool is thin gets a short stage, never padding:
# `hard` is `None` where the ledger states nothing that makes a stage hard, and the page then
# renders the designed `.empty` block instead of inventing a difficulty.
CASE_STAGES: dict[str, dict] = {
    "sama-soc-triage": {
        "problem": ("Security operations triage is the work: an agentic triage and response "
                    "automation system runs a multistage agentic triage workflow.",
                    ["L4.1"]),
        "approach": ("Context construction, active investigation, threat modeling, quality guards, "
                     "and verdict generation — with typed contracts and grounding controls around "
                     "every stage.", ["L4.1", "L4.1@4.1"]),
        "hard": ("Grounding and evidence controls have to hold at every stage, so the output stays "
                 "traceable to its source.", ["L4.1"]),
        "outcome": ("Verdict generation at the end of an evaluation-gated workflow: LLM-as-judge "
                    "checks, RAGAS and blind-vs-shown evals, plus contract, adversarial and "
                    "compliance test suites.", ["L4.1@4.1", "L3.4"]),
    },
    "smartops-soc-app": {
        "problem": ("Investigation has to be brokered: a task broker coordinates domain analysts.",
                    ["L4.2"]),
        "approach": ("Findings are evidence-linked and carried in replayable traces, with "
                     "hypothesis-blind analysis and VirusTotal enrichment.", ["L4.2", "L4.2@4.1"]),
        "hard": ("Hypothesis-blind analysis across domain analysts, with findings that stay "
                 "evidence-linked.", ["L4.2", "L4.2@4.1"]),
        "outcome": ("A brokered multi-agent investigation platform whose traces can be replayed.",
                    ["L4.2"]),
    },
    "milo-ai-employee": {
        "problem": ("An operations teammate acts, so its autonomy has to be bounded by design "
                    "rather than assumed.", ["L4.3"]),
        "approach": ("Approval binding, authority boundaries, redaction and budget/time limits "
                     "bound every action; the incidents are simulated Splunk/Cribl.",
                    ["L4.3"]),
        "hard": ("Actions are idempotent and reconciled, and the agent skills are versioned behind "
                 "evaluation gates.", ["L4.3@4.1"]),
        "outcome": ("A safety-first agentic operations teammate over simulated Splunk/Cribl "
                    "incidents.", ["L4.3"]),
    },
    "pulsesec": {
        "problem": ("One copilot has to serve several domains without one domain's schema leaking "
                    "into another's.", ["L4.4"]),
        "approach": ("A domain-pack architecture with MCP connectors and schema-grounded query "
                     "generation, handling timelines and cases under guardrails.", ["L4.4"]),
        "hard": ("Evaluation harnesses and E2E coverage target grounding, pack selection, and "
                 "guardrails.", ["L4.4@4.1"]),
        "outcome": ("A multi-domain investigation copilot with a React/Vite UI and agent-trace "
                    "telemetry.", ["L4.4"]),
    },
    "tonsy-gpt": {
        "problem": ("Retrieval quality is the product: one retriever is not enough, and the "
                    "assistant is self-hosted.", ["L4.5"]),
        "approach": ("Hybrid BM25 + ChromaDB retrieval, RRF (reciprocal-rank fusion), neural "
                     "reranking and semantic caching, behind FastAPI/SSE and Next.js.",
                    ["L4.5", "L5.1"]),
        "hard": ("Parent-setting expansion and session state, carried by a FastAPI/SSE backend "
                 "with session persistence.", ["L4.5@4.1"]),
        "outcome": ("A self-hosted RAG assistant.", ["L4.5"]),
    },
    "smart-care": {
        "problem": ("Analytics questions arrive in intent, not SQL, and the answer has to be "
                    "grounded.", ["L4.6"]),
        "approach": ("Intent → grounded SQL → stats → visualisation agents, on Dremio with a "
                     "streaming React UI.", ["L4.6"]),
        "hard": ("An orchestrator with shared state, schema-aware prompting and session memory "
                 "coordinates the chain.", ["L4.6@4.1"]),
        "outcome": ("A network-ops analytics copilot.", ["L4.6"]),
    },
    "halalbot": {
        "problem": ("Ordering happens in WhatsApp, and the product has to ship to a phone.",
                    ["L4.7"]),
        "approach": ("A shipped WhatsApp ordering product with a signed Android APK, an owner "
                     "dashboard and Arabic/English parsing, validated over a live tunnel.",
                    ["L4.7"]),
        "hard": ("Two production bugs agents' own tests blessed — root-caused from live logs, "
                 "pinned as regression tests.", ["L4.7@4.1"]),
        "outcome": ("A shipped product: signed Android APK, owner dashboard, 65-test suite.",
                    ["L4.7"]),
    },
    "forwheelz": {
        "problem": ("Risk has to be read from vehicle telemetry, and the output has to be usable "
                    "by an insurer's API.", ["L4.8"]),
        "approach": ("A 28-feature trip pipeline from vehicle telemetry into RF/XGBoost with "
                     "ablation, behind explicit output contracts.", ["L4.8"]),
        "hard": ("Models were evaluated through feature ablations and error analysis.",
                 ["S5-P3"]),
        "outcome": ("Driver-risk intelligence with a risk-index + DNA-score, and "
                    "production-oriented outputs for confidence and risk contributors.",
                    ["L4.8@4.1", "S5-P3"]),
    },
    "email-mcp": {
        "problem": ("Tools are the interface: an MCP tool server.", ["L4.9"]),
        "approach": ("A documented MCP tool server with 29 tests.", ["L4.9"]),
        "hard": None,
        "outcome": ("An MCP tool server, documented, with 29 tests.", ["L4.9"]),
    },
    "voice-agent-core": {
        "problem": ("Speech has to move through a pipeline before a model can answer.",
                    ["L4.10"]),
        "approach": ("VAD → Whisper → LLM → TTS, Twilio-ready, covering Arabic + English.",
                     ["L4.10"]),
        "hard": None,
        "outcome": ("A voice agent pipeline that is Twilio-ready and covers Arabic + English.",
                    ["L4.10"]),
    },
}
