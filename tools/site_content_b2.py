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

ROLE_LEDGER = b("AI Solutions Engineer", ["L3.1"], "verbatim",
                "The ledger's own role row (L3.1). Used for the at-a-glance strip, so the strip "
                "carries the ledger's exact role token rather than the longer S5 title.")

# ---------------------------------------------------------------- section serials & decks

SERIALS = {
    "about": b("01 / 07", [], "structural",
               "Section serial. A structural position marker for the section, not a claim."),
    "experience": b("02 / 07", [], "structural", "Section serial."),
    "work": b("03 / 07", [], "structural", "Section serial."),
    "evidence": b("04 / 07", [], "structural", "Section serial."),
    "skills": b("05 / 07", [], "structural", "Section serial."),
    "education": b("06 / 07", [], "structural", "Section serial."),
    "contact": b("07 / 07", [], "structural", "Section serial."),
}

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
    "evidence_deck": b("One system, drawn from published material.", [], "structural"),
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
    "legend_h": b("Source tiers", [], "structural",
                  "Process metadata: the ledger's own Sources table, restated."),
    "legend_s1": b("S1 — authorized LinkedIn profile", [], "structural"),
    "legend_s2": b("S2 — owner résumé", [], "structural"),
    "legend_s3": b("S3 — owner profile material", [], "structural"),
    "legend_s5": b("S5 — owner résumé (newer)", [], "structural"),
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

# The attribution-rule tag expansion: a structural statement of where the adjacent block comes
# from. Rendered visually-hidden beside the tier token.
SOURCE_TAGS = {
    "S1": b("— source: authorized LinkedIn profile", [], "structural"),
    "S2": b("— source: owner résumé", [], "structural"),
    "S3": b("— source: owner profile material", [], "structural"),
    "S5": b("— source: owner résumé (newer)", [], "structural"),
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
