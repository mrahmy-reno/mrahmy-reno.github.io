"""Content model for the Benchmark #1 portfolio.

Every rendered string is declared here with:
  text  - the exact plain text that will appear on the page (HTML-escaped at render time)
  refs  - the FACTS_LEDGER.md row id(s) that authorise it
  mode  - "verbatim"   : reproduces the ledger string (case/punctuation only adjusted)
          "composed"   : built under PRD R2 from ledger phrases only (phrases named in the note)
          "structural" : a heading/label/navigation string that asserts no fact
          "print"      : print-only variant of mapped strings (still mapped)
  note  - composition note, required for "composed"

Ref ids:
  L1.1-L1.5 identity/headline   L2.1 positioning (S3)   L2.2 resume summary (S2)
  L3.1-L3.3 roles               L3.4 bullets block      L4.1-L4.10 projects
  L5.1 skills                   L6.1-L6.2 education     L7.1-L7.5 Tier-A certs
  L8.1/L8.2 Tier C contact (never rendered in the delivered state)   L8.3 LinkedIn

  A ref suffixed "@4.1"  -> ledger section 4.1 approved extension text.
  A ref beginning "S5"   -> FACTS_LEDGER.md section 11 (source S5, "Resume Pro"), which is
                            authoritative where it differs from S2/S3. The explicit ids used:
       S5-R2  current job title          S5-R3  SEWS-E end date
       S5-R4  SEWS-E employer name       S5-R6  Cribl wording + date
       S5-R9  summary/positioning        S5-R10 experience bullets
       S5-P1  Renosystems bullets        S5-P2  SEWS-E bullets
       S5-P3  ForWheelz wording          S5-P4  certification dates
       S5-P5  education dates            S5-P6  skills additions
"""


def b(text, refs, mode="verbatim", note=None):
    return {"text": text, "refs": list(refs), "mode": mode, "note": note}


# ---------------------------------------------------------------- global strings

NAME = b("Mohammed Tawfiq Rahmy", ["L1.1"])
HEADLINE = b("Solutions Engineer | Mechatronics × AI Systems", ["L1.2"],
             "verbatim",
             "The live LinkedIn headline (S1). R9: the hero headline stays this string even "
             "though S5 has a newer keyword line.")
LOCATION = b("New Cairo, Egypt", ["L1.4"])
FOCUS = b(
    "multi-agent orchestration, RAG, MCP tooling, evaluation harnesses, and safety guardrails",
    ["L2.2"],
)
LANGUAGES = b("Arabic (native) · English (C1) · German (A2)", ["L5.1"])
CURRENT_ROLE = b("Associate Solutions Engineer — AI / GenAI Solutions", ["S5-R2"])
CURRENT_EMPLOYER = b("Renosystems", ["L3.1", "S5-R1"])
CURRENT_DATES = b("Mar 2026 – Present", ["L3.1"])
CURRENT_ROLE_SHORT = b("Associate Solutions Engineer", ["S5-R2"])

META_DESCRIPTION = b(
    "I build agentic and generative AI systems for security, operations, and analytics. "
    "Hands-on with Amazon Bedrock, Strands Agents, multi-agent orchestration, RAG, MCP/tool "
    "integrations, LLM evaluation, guardrails, and full-stack AI delivery.",
    ["S5-R9"],
    "composed",
    "B2-04 / D11 repair: the S5 summary with its opening clause recast to a first-person, "
    "non-title phrase — 'I build …' replaces 'AI Solutions Engineer building …' — so that the "
    "meta description no longer repeats the job title beside the <title> field in a search "
    "result or link preview. Every substantive word after the opening clause is the S5 summary's "
    "own (the closing clause about certifications is rendered in About). No new fact is added.",
)

LINKEDIN_URL = "https://www.linkedin.com/in/mohammed-rahmy"          # L8.3
LINKEDIN_SHORT = b("linkedin.com/in/mohammed-rahmy", ["L8.3"])

PITCH = b(
    "AI Solutions Engineer who ships production agentic systems. I've built multi-agent "
    "platforms for security operations and safety-first AI teammates with typed contracts, "
    "grounding, evaluation gates, and approval binding, and I've shipped independent products "
    "where coding agents wrote most of the code under my direction (65-test suites, signed "
    "APKs, live dashboards). Enterprise discipline + builder velocity.",
    ["L2.1"],
    "composed",
    "L2.1 verbatim with the two ledger elisions resolved to the words present at those exact "
    "positions in the source the ledger cites (PRD E1: 'I've built' / 'and I've shipped'). No "
    "other text added. Declared composition exception E1.",
)

S5_SUMMARY = b(
    "AI Solutions Engineer building agentic and generative AI systems for security, operations, "
    "and analytics. Hands-on with Amazon Bedrock, Strands Agents, multi-agent orchestration, RAG, "
    "MCP/tool integrations, LLM evaluation, guardrails, and full-stack AI delivery; backed by AWS "
    "Professional and Associate certifications.",
    ["S5-R9"],
    "verbatim",
    "The S5 summary, rendered verbatim in About (resolution R9: S5 summary feeds the "
    "About/positioning).",
)

ABOUT_SUMMARY = b(
    "AI Solutions Engineer building production agentic systems: multi-agent orchestration, RAG, "
    "MCP tooling, evaluation harnesses, and safety guardrails. Enterprise-grade grounding and "
    "test discipline from security-operations work; ships complete products (backend, UI, "
    "mobile) with AI coding agents.",
    ["L2.2"],
    "verbatim",
    "L2.2 verbatim (retained: S5 does not contradict it, it describes the same work).",
)

# ---------------------------------------------------------------- structural labels

L = {
    "skip": b("Skip to content", [], "structural"),
    "nav_about": b("About", [], "structural"),
    "nav_experience": b("Experience", [], "structural"),
    "nav_work": b("Work", [], "structural"),
    "nav_skills": b("Skills", [], "structural"),
    "nav_education": b("Education", [], "structural"),
    "nav_contact": b("Contact", [], "structural"),
    "menu": b("Menu", [], "structural"),
    "header_contact": b("LinkedIn", ["L8.3"], "structural",
                        "Link text is the platform name; href is the L8.3 URL."),
    "h2_about": b("About", [], "structural"),
    "h2_experience": b("Experience", [], "structural"),
    "h2_work": b("Selected work", [], "structural"),
    "h2_skills": b("Skills", [], "structural"),
    "h2_education": b("Education & certifications", [], "structural"),
    "h2_certs": b("Certifications", [], "structural"),
    "h2_contact": b("Contact", [], "structural"),
    "fact_current": b("Current", [], "structural"),
    "fact_based": b("Based in", [], "structural"),
    "fact_focus": b("Focus", [], "structural"),
    "fact_languages": b("Languages", [], "structural"),
    "cta_work": b("See selected work", [], "structural"),
    "cta_linkedin": b("Connect on LinkedIn", ["L8.3"], "structural",
                      "Link text is a call to action; href is the L8.3 URL."),
    "back_to_top": b("Back to top", [], "structural"),
    "all_work": b("All work", [], "structural"),
    "prev": b("Previous project", [], "structural"),
    "next": b("Next project", [], "structural"),
    "overview": b("Overview", [], "structural"),
    "capabilities": b("Capabilities & practices", [], "structural"),
    "contact_linkedin_text": b("Connect with me on LinkedIn", ["L8.3"], "structural",
                               "Link text is a call to action; href is the L8.3 URL."),
    "contact_default_note": b("This site links to LinkedIn only.", [], "structural",
                              "Statement about this site's configured state, not a claim about "
                              "the person."),
    "footer_provenance": b("Every claim on this site is sourced.", [], "structural",
                           "Process statement about this site; true by construction (A1)."),
    "copyright": b("© Mohammed Tawfiq Rahmy", ["L1.1"], "structural",
                   "Name only; deliberately no year token (PRD 4.8)."),
    "nf_h1": b("Page not found", [], "structural"),
    "nf_body": b("The page you were looking for is not on this site.", [], "structural"),
    "nf_link": b("Back to the home page", [], "structural"),
    "projects_intro": b("Ten projects: security-operations agents, applied RAG and analytics, "
                        "and shipped products.", ["L4.1", "L4.2", "L4.3", "L4.4", "L4.5",
                                                  "L4.6", "L4.7", "L4.8", "L4.9", "L4.10"],
                        "composed",
                        "Structural enumeration of the ten ledger project rows; 'ten' equals the "
                        "rendered card count (checked by the coverage test)."),
    "g1": b("Security operations & agent safety", [], "structural"),
    "g2": b("Applied RAG & analytics", [], "structural"),
    "g3": b("Shipped products & ML systems", [], "structural"),
    "featured": b("Featured", [], "structural"),
    "tech_line_label": b("Technology", [], "structural"),
    "row_open": b("Open", [], "structural",
                  "Link text on a project row; the accessible name also carries the project "
                  "name."),
    "stage_problem": b("Problem", [], "structural"),
    "stage_approach": b("Approach", [], "structural"),
    "stage_architecture": b("Architecture", [], "structural"),
    "stage_hard": b("The hard part", [], "structural"),
    "stage_evidence": b("Evidence", [], "structural"),
    "stage_outcome": b("Outcome", [], "structural"),
    "newtab": b("(opens in a new tab)", [], "structural",
                "Accessible-name suffix on every link that opens a new tab."),
}

# ---------------------------------------------------------------- experience

EXPERIENCE = [
    {
        "title": b("Associate Solutions Engineer — AI / GenAI Solutions", ["S5-R2"]),
        "employer": b("Renosystems", ["L3.1", "S5-R1"]),
        "dates": b("Mar 2026 – Present", ["L3.1"]),
        "bullets": [
            b("Architect and implement evidence-grounded multi-agent SOC workflows using Strands "
              "Agents, Amazon Bedrock, Splunk/MCP integrations, and SOAR playbooks, with typed "
              "contracts, quality guards, verdict generation, and controlled write-back.",
              ["S5-P1"], "verbatim",
              "S5 Renosystems bullet 1 (FACTS_LEDGER section 11, S5-P1). Describes the work "
              "without naming any project (D17 attribution guard preserved)."),
            b("Build brokered investigation systems that decompose tasks across specialist "
              "agents while enforcing scope, attribution, grounding, evidence-link integrity, "
              "replayable traces, and adversarial/compliance tests.",
              ["S5-P1"], "verbatim",
              "S5 Renosystems bullet 2 (S5-P1). No project name asserted."),
            b("Develop AI copilots across Splunk, Axiom, and Dremio with schema-grounded "
              "query/SQL generation, validation, visualization, session memory, telemetry, and "
              "React/Vite interfaces.", ["S5-P1"], "verbatim",
              "S5 Renosystems bullet 3 (S5-P1). No project name asserted."),
            b("Engineer and evaluate RAG/agent stacks using BM25 + ChromaDB hybrid retrieval, "
              "reciprocal-rank fusion, neural reranking, semantic caching, RAGAS, LLM-as-judge "
              "validation, approval boundaries, and automated E2E gates.",
              ["S5-P1"], "verbatim",
              "S5 Renosystems bullet 4 (S5-P1). No project name asserted."),
        ],
    },
    {
        "title": b("Automotive Drawing Office Engineer", ["L3.2"]),
        "employer": b("Sumitomo Electric Wiring Systems – Europe (SEWS-E), Cairo",
                      ["L3.2", "S5-R4"]),
        "dates": b("May 2024 – Feb 2026", ["L3.2", "S5-R3"]),
        "bullets": [
            b("Implement wiring-harness engineering changes from OEM documentation (DCS/PPMR, "
              "ECR) for Toyota, Stellantis, and Ford; produce BOMs, man-hour reports, and splice "
              "diagrams with production traceability.",
              ["L3.4", "S5-P2"], "composed",
              "Phrases: 'harness design changes from OEM documentation (DCS/PPMR, ECR) for "
              "Toyota, Stellantis, and Ford' (L3.4); 'produced BOMs, man-hour reports, and "
              "splice diagrams with production traceability' (S5-P2). Tense unified; no new "
              "noun, number or scope added."),
            b("Coordinate design and production stakeholders to troubleshoot technical issues "
              "and validate updates against cost, quality, and manufacturability constraints.",
              ["S5-P2"], "verbatim",
              "S5 SEWS-E bullet 2 (S5-P2)."),
        ],
    },
    {
        "title": b("Nano-Robotics Researcher", ["L3.3"]),
        "employer": b("MNR Lab (Cairo)", ["L3.3"]),
        "dates": b("Jun 2022 – Sep 2022", ["L3.3"]),
        "bullets": [
            b("Biocompatible magneto-sperm fabrication via electrospinning, and a 4-coil "
              "electromagnetic control system with closed-loop positioning (Arduino, OpenCV).",
              ["L3.4"], "verbatim",
              "Retained per resolution R5: S5 omits this role for brevity, nothing contradicts "
              "it."),
        ],
    },
]

# ---------------------------------------------------------------- skills (L5.1 + S5-P6)

SKILL_GROUPS = [
    ("Agentic AI", [
        ("multi-agent orchestration (Strands Agents)", ["L5.1"]),
        ("Claude Code / coding-agent workflows", ["L5.1"]),
        ("MCP servers", ["L5.1"]),
        ("agent evals (LLM-as-judge, RAGAS, blind-vs-shown)", ["L5.1"]),
        ("approval binding & safety boundaries", ["L5.1"]),
        ("grounding/evidence controls", ["L5.1"]),
        ("LangChain", ["S5-P6"]),
    ]),
    ("RAG", [
        ("ChromaDB", ["L5.1"]),
        ("BM25 + reciprocal-rank fusion", ["L5.1"]),
        ("RRF", ["S5-P6"]),
        ("neural reranking", ["L5.1"]),
        ("FAISS", ["L5.1"]),
        ("semantic caching", ["L5.1"]),
    ]),
    ("LLM platforms", [
        ("Amazon Bedrock", ["L5.1"]),
        ("Azure OpenAI", ["L5.1"]),
        ("Gemini", ["L5.1"]),
        ("OpenAI", ["L5.1"]),
        ("DeepSeek", ["L5.1"]),
    ]),
    ("Backend & data", [
        ("Python (asyncio, FastAPI, SSE)", ["L5.1"]),
        ("TypeScript", ["L5.1"]),
        ("Splunk", ["L5.1"]),
        ("Cribl", ["L5.1"]),
        ("Elasticsearch", ["L5.1"]),
        ("Dremio", ["L5.1"]),
        ("Axiom", ["S5-P6"]),
        ("Pydantic", ["L5.1"]),
        ("SQL", ["L5.1"]),
        ("SQLite", ["S5-P6"]),
        ("REST APIs", ["S5-P6"]),
        ("Docker", ["L5.1"]),
    ]),
    ("Frontend & mobile", [
        ("React/Vite", ["L5.1"]),
        ("Vite", ["S5-P6"]),
        ("Next.js", ["L5.1"]),
        ("Android WebView packaging & signing", ["L5.1"]),
    ]),
    ("ML/CV", [
        ("scikit-learn", ["L5.1"]),
        ("XGBoost", ["L5.1"]),
        ("Random Forest", ["S5-P6"]),
        ("SentenceTransformers", ["S5-P6"]),
        ("OpenCV", ["L5.1"]),
        ("feature engineering", ["L5.1"]),
    ]),
    ("Also", [
        ("WhatsApp Business Cloud API", ["L5.1"]),
        ("Twilio voice pipelines", ["L5.1"]),
        ("Git/GitHub", ["L5.1"]),
        ("web scraping", ["L5.1"]),
        ("Pytest", ["S5-P6"]),
        ("Playwright", ["S5-P6"]),
    ]),
    ("Languages", [
        ("Arabic (native)", ["L5.1"]),
        ("English (C1)", ["L5.1"]),
        ("German (A2)", ["L5.1"]),
    ]),
]

# ---------------------------------------------------------------- education / certifications

EDUCATION = [
    {
        "institution": b("American University in Cairo", ["L6.1"]),
        "credential": b("CND Digital IC Design Diploma", ["L6.1"]),
        "detail": b("ASIC RTL-to-GDSII · Verilog/SystemVerilog · Synopsys", ["L6.1"]),
        "year": b("Sep 2023 – Aug 2024", ["S5-P5"]),
    },
    {
        "institution": b("German University in Cairo", ["L6.2"]),
        "credential": b("BSc Mechatronics Engineering", ["L6.2"]),
        "detail": b("Thesis: magneto-sperm fabrication & characterisation", ["L6.2"]),
        "year": b("Oct 2018 – Jun 2023", ["S5-P5"]),
    },
]

CERTIFICATIONS = [
    (b("AWS Certified Generative AI Developer – Professional (AIP-C01)", ["L7.1"]),
     b("Amazon Web Services", ["L7.1"]),
     b("Jul 2026", ["S5-P4"])),
    (b("AWS Certified Machine Learning Engineer – Associate (MLA-C01)", ["L7.2"]),
     b("Amazon Web Services", ["L7.2"]),
     b("May 2026", ["S5-P4"])),
    (b("AWS Certified Solutions Architect – Associate (SAA-C03)", ["L7.3"]),
     b("Amazon Web Services", ["L7.3"]),
     b("Apr 2026", ["S5-P4"])),
    (b("Cribl Certified Admin – Stream", ["L7.4", "S5-R6"]),
     b("Cribl", ["L7.4"]),
     b("Jun 2026", ["S5-P4"])),
    (b("Generative AI with AWS", ["L7.5"]),
     b("Udacity", ["L7.5"]),
     None),
]

# ---------------------------------------------------------------- projects

SCOPE_NOTE = b(
    "Describes capability and engineering practice; no client or third-party internals are "
    "disclosed.",
    [],
    "structural",
    "Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person.",
)

PROJECTS = [
    {
        "slug": "sama-soc-triage",
        "name": b("SAMA — Agentic SOC Triage & Response Automation", ["L4.1"]),
        "one_liner": b("Multistage agentic triage workflow, grounding/evidence controls, "
                       "typed contracts.", ["L4.1"]),
        "group": 1,
        "featured": True,
        "tech_line": [
            b("Strands Agents", ["L3.4"]),
            b("Amazon Bedrock", ["L3.4"]),
            b("MCP connectors", ["L3.4"]),
        ],
        "overview": [
            b("An agentic triage and response automation system for security operations. It "
              "runs a multistage agentic triage workflow built on Strands Agents and Amazon "
              "Bedrock, with MCP connectors, typed contracts and grounding controls.",
              ["L4.1", "L3.4"], "composed",
              "Phrases: 'agentic ... Triage & Response Automation' (L4.1 row name), 'security "
              "operations' (L3.4), 'multistage agentic triage workflow' (L4.1), 'Strands "
              "Agents', 'Amazon Bedrock', 'MCP connectors', 'typed contracts', 'grounding "
              "controls' (L4.1/L3.4). Connective verbs only."),
            b("The workflow covers context construction, active investigation, threat modeling, "
              "quality guards, and verdict generation, and it was developed under evaluation "
              "gates: LLM-as-judge checks, RAGAS and blind-vs-shown evals, plus contract, "
              "adversarial and compliance test suites.",
              ["L4.1@4.1", "L3.4"], "composed",
              "Phrases: 'context construction, active investigation, threat modeling, quality "
              "guards, and verdict generation' (ledger 4.1, SAMA row), 'LLM-as-judge', 'RAGAS', "
              "'blind-vs-shown', 'contract/adversarial/compliance suites' (L3.4)."),
            b("Grounding/evidence controls keep its output traceable to its source.",
              ["L4.1"], "composed",
              "Phrases: 'grounding/evidence controls' (L4.1). No claim about the client, its "
              "data, its environment or its outcomes (SAMA rule: mention depth, never "
              "internals)."),
        ],
        "capabilities": [
            b("Multistage agentic triage workflow", ["L4.1"]),
            b("Multi-agent triage, investigation and response", ["L3.4"]),
            b("Context construction, active investigation, threat modeling, quality guards, and "
              "verdict generation", ["L4.1@4.1"]),
            b("Grounding and evidence controls", ["L4.1"]),
            b("Typed contracts", ["L4.1"]),
            b("Strands Agents and Amazon Bedrock", ["L3.4"]),
            b("MCP connectors", ["L3.4"]),
            b("LLM-as-judge checks, RAGAS, blind-vs-shown evals", ["L3.4"]),
            b("Contract, adversarial and compliance test suites", ["L3.4"]),
        ],
    },
    {
        "slug": "smartops-soc-app",
        "name": b("SmartOps SOC App", ["L4.2"]),
        "one_liner": b("Brokered multi-agent investigation platform: task broker, domain "
                       "analysts, evidence-linked findings, replayable traces.", ["L4.2"]),
        "group": 1,
        "featured": True,
        "tech_line": [],
        "overview": [
            b("A brokered multi-agent investigation platform. A task broker coordinates domain "
              "analysts, and findings are evidence-linked and carried in replayable traces.",
              ["L4.2"], "composed",
              "Phrases: 'brokered multi-agent investigation platform', 'task broker', 'domain "
              "analysts', 'evidence-linked findings', 'replayable traces' (L4.2)."),
            b("It supports hypothesis-blind analysis, replayable traces, and VirusTotal "
              "enrichment.", ["L4.2@4.1"], "composed",
              "Phrases: 'hypothesis-blind analysis, replayable traces, and VirusTotal "
              "enrichment' (ledger 4.1, SmartOps row)."),
        ],
        "capabilities": [
            b("Brokered multi-agent investigation platform", ["L4.2"]),
            b("Task broker", ["L4.2"]),
            b("Domain analysts", ["L4.2"]),
            b("Evidence-linked findings", ["L4.2"]),
            b("Replayable traces", ["L4.2"]),
            b("Hypothesis-blind analysis", ["L4.2@4.1"]),
            b("VirusTotal enrichment", ["L4.2@4.1"]),
        ],
    },
    {
        "slug": "milo-ai-employee",
        "name": b("Milo AI Employee", ["L4.3"]),
        "one_liner": b("Safety-first agentic operations teammate over simulated Splunk/Cribl "
                       "incidents; approval binding, authority boundaries, redaction, "
                       "budget/time limits.", ["L4.3"]),
        "group": 1,
        "featured": True,
        "tech_line": [
            b("Simulated Splunk", ["L4.3"]),
            b("Cribl", ["L4.3"]),
        ],
        "overview": [
            b("A safety-first agentic operations teammate that works over simulated Splunk and "
              "Cribl incidents. Actions carry approval binding and the agent operates inside "
              "authority boundaries with redaction and budget/time limits, so its autonomy is "
              "bounded by design rather than assumed.", ["L4.3"], "composed",
              "Phrases: 'safety-first agentic operations teammate', 'simulated Splunk/Cribl "
              "incidents', 'approval binding', 'authority boundaries', 'redaction', "
              "'budget/time limits' (L4.3)."),
            b("Its actions are idempotent and reconciled, and it runs on versioned agent skills "
              "behind evaluation gates.", ["L4.3@4.1"], "composed",
              "Phrases: 'idempotent actions and reconciliation'; 'versioned agent skills, "
              "evaluation gates' (ledger 4.1, Milo row)."),
        ],
        "capabilities": [
            b("Safety-first agentic operations teammate", ["L4.3"]),
            b("Simulated Splunk and Cribl incidents", ["L4.3"]),
            b("Approval binding", ["L4.3"]),
            b("Authority boundaries", ["L4.3"]),
            b("Redaction", ["L4.3"]),
            b("Budget and time limits", ["L4.3"]),
            b("Idempotent actions and reconciliation", ["L4.3@4.1"]),
            b("Versioned agent skills, evaluation gates", ["L4.3@4.1"]),
        ],
    },
    {
        "slug": "pulsesec",
        "name": b("PulseSec", ["L4.4"]),
        "one_liner": b("Multi-domain investigation copilot: domain-pack architecture, MCP "
                       "connectors, schema-grounded query generation, React/Vite UI with "
                       "agent-trace telemetry.", ["L4.4"]),
        "group": 1,
        "featured": True,
        "tech_line": [
            b("MCP connectors", ["L4.4"]),
            b("React/Vite", ["L4.4"]),
        ],
        "overview": [
            b("A multi-domain investigation copilot built on a domain-pack architecture, with "
              "MCP connectors and schema-grounded query generation.", ["L4.4"], "composed",
              "Phrases: 'multi-domain investigation copilot', 'domain-pack architecture', 'MCP "
              "connectors', 'schema-grounded query generation' (L4.4)."),
            b("It handles timeline/case handling under guardrails, and exposes a React/Vite UI "
              "with agent-trace telemetry.", ["L4.4", "L4.4@4.1"], "composed",
              "Phrases: 'timeline/case handling, guardrails' (ledger 4.1, PulseSec row); "
              "'React/Vite UI with agent-trace telemetry' (L4.4)."),
            b("Evaluation harnesses and E2E coverage target grounding, pack selection, and "
              "guardrails.", ["L4.4@4.1"], "composed",
              "Phrases: 'evaluation harnesses and E2E coverage for grounding, pack selection, "
              "and guardrails' (ledger 4.1, PulseSec row)."),
        ],
        "capabilities": [
            b("Multi-domain investigation copilot", ["L4.4"]),
            b("Domain-pack architecture", ["L4.4"]),
            b("MCP connectors", ["L4.4"]),
            b("Schema-grounded query generation", ["L4.4"]),
            b("React/Vite UI with agent-trace telemetry", ["L4.4"]),
            b("Timeline/case handling, guardrails", ["L4.4@4.1"]),
            b("Evaluation harnesses and E2E coverage for grounding, pack selection, and "
              "guardrails", ["L4.4@4.1"]),
        ],
    },
    {
        "slug": "tonsy-gpt",
        "name": b("Tonsy-GPT", ["L4.5"]),
        "one_liner": b("Self-hosted RAG assistant: hybrid BM25 + ChromaDB, RRF, neural "
                       "reranking, semantic caching, FastAPI/SSE + Next.js.", ["L4.5"]),
        "group": 2,
        "featured": False,
        "tech_line": [
            b("BM25", ["L4.5"]),
            b("ChromaDB", ["L4.5"]),
            b("FastAPI/SSE", ["L4.5"]),
            b("Next.js", ["L4.5"]),
        ],
        "overview": [
            b("A self-hosted RAG assistant. Retrieval is hybrid BM25 + ChromaDB with RRF "
              "(reciprocal-rank fusion), plus neural reranking and semantic caching, behind a "
              "FastAPI/SSE + Next.js stack.", ["L4.5", "L5.1"], "composed",
              "Phrases: 'self-hosted RAG assistant', 'hybrid BM25 + ChromaDB', 'RRF', 'neural "
              "reranking', 'semantic caching', 'FastAPI/SSE + Next.js' (L4.5). 'reciprocal-rank "
              "fusion' expands the acronym using the L5.1 skills wording, as PRD 4.5 permits."),
            b("Retrieval supports parent-setting expansion, and session state is carried by a "
              "FastAPI/SSE backend with session persistence.", ["L4.5@4.1"], "composed",
              "Phrases: 'parent-setting expansion'; 'FastAPI/SSE backend with session "
              "persistence' (ledger 4.1, Tonsy-GPT row)."),
        ],
        "capabilities": [
            b("Self-hosted RAG assistant", ["L4.5"]),
            b("Hybrid BM25 + ChromaDB", ["L4.5"]),
            b("RRF retrieval fusion", ["L4.5"]),
            b("Neural reranking", ["L4.5"]),
            b("Semantic caching", ["L4.5"]),
            b("FastAPI/SSE + Next.js", ["L4.5"]),
            b("Parent-setting expansion", ["L4.5@4.1"]),
            b("FastAPI/SSE backend with session persistence", ["L4.5@4.1"]),
        ],
    },
    {
        "slug": "smart-care",
        "name": b("Smart Care", ["L4.6"]),
        "one_liner": b("Network-ops analytics copilot: intent → grounded SQL → stats → "
                       "visualisation agents, Dremio, streaming React UI.", ["L4.6"]),
        "group": 2,
        "featured": False,
        "tech_line": [
            b("Dremio", ["L4.6"]),
            b("React", ["L4.6"]),
        ],
        "overview": [
            b("A network-ops analytics copilot that chains intent → grounded SQL → stats → "
              "visualisation agents, on Dremio with a streaming React UI.", ["L4.6"], "composed",
              "Phrases: 'network-ops analytics copilot', 'intent → grounded SQL → stats → "
              "visualisation agents', 'Dremio', 'streaming React UI' (L4.6)."),
            b("An orchestrator with shared state, schema-aware prompting and session memory "
              "coordinates the chain.", ["L4.6@4.1"], "composed",
              "Phrases: 'orchestrator + shared state, schema-aware prompting, session memory' "
              "(ledger 4.1, Smart Care row)."),
        ],
        "capabilities": [
            b("Network-ops analytics copilot", ["L4.6"]),
            b("Intent → grounded SQL → stats → visualisation agents", ["L4.6"]),
            b("Dremio", ["L4.6"]),
            b("Streaming React UI", ["L4.6"]),
            b("Orchestrator + shared state", ["L4.6@4.1"]),
            b("Schema-aware prompting", ["L4.6@4.1"]),
            b("Session memory", ["L4.6@4.1"]),
        ],
    },
    {
        "slug": "halalbot",
        "name": b("HalalBot", ["L4.7"]),
        "one_liner": b("Shipped WhatsApp ordering product (signed Android APK, owner dashboard, "
                       "65-test suite, Arabic/English parsing, live tunnel E2E).", ["L4.7"]),
        "group": 3,
        "featured": False,
        "tech_line": [
            b("WhatsApp", ["L4.7"]),
            b("Android APK", ["L4.7"]),
        ],
        "overview": [
            b("A shipped WhatsApp ordering product with a signed Android APK, an owner dashboard "
              "and a 65-test suite.", ["L4.7"], "composed",
              "Phrases: 'shipped WhatsApp ordering product', 'signed Android APK', 'owner "
              "dashboard', '65-test suite' (L4.7)."),
            b("It runs Arabic/English parsing, the end-to-end path was validated over a live "
              "tunnel, and the stack spans Python/FastAPI, React and mobile packaging.",
              ["L4.7", "L3.4"], "composed",
              "Phrases: 'Arabic/English parsing', 'live tunnel E2E' (L4.7); 'Python/FastAPI, "
              "React, mobile packaging' (L3.4)."),
            b("Two production bugs agents' own tests blessed — root-caused from live logs, "
              "pinned as regression tests.", ["L4.7@4.1"], "composed",
              "Phrases: 'two production bugs agents' own tests blessed … root-caused from live "
              "logs, pinned as regression tests' (ledger 4.1, HalalBot row). The ledger's "
              "elision marker is rendered as an em dash and nothing else is changed."),
        ],
        "capabilities": [
            b("Shipped WhatsApp ordering product", ["L4.7"]),
            b("Signed Android APK", ["L4.7"]),
            b("Owner dashboard", ["L4.7"]),
            b("65-test suite", ["L4.7"]),
            b("Arabic/English parsing", ["L4.7"]),
            b("Live tunnel E2E", ["L4.7"]),
            b("Python/FastAPI, React, mobile packaging", ["L3.4"]),
            b("Two production bugs agents' own tests blessed — root-caused from live logs, "
              "pinned as regression tests", ["L4.7@4.1"]),
        ],
    },
    {
        "slug": "forwheelz",
        "name": b("ForWheelz", ["L4.8"]),
        "one_liner": b("Driver-risk intelligence: 28-feature trip pipeline from vehicle "
                       "telemetry, RF/XGBoost with ablation, output contracts.", ["L4.8"]),
        "group": 3,
        "featured": False,
        "tech_line": [b("RF/XGBoost", ["L4.8"])],
        "overview": [
            b("Driver-risk intelligence built on a 28-feature trip pipeline from vehicle "
              "telemetry, with RF/XGBoost with ablation and explicit output contracts.",
              ["L4.8"], "composed",
              "Phrases: 'driver-risk intelligence', '28-feature trip pipeline from vehicle "
              "telemetry', 'RF/XGBoost with ablation', 'output contracts' (L4.8)."),
            b("Random Forest/XGBoost models were evaluated through feature ablations and error "
              "analysis, and production-oriented outputs were defined for confidence, risk "
              "contributors, and insurer/API integration.", ["S5-P3"], "verbatim",
              "S5 ForWheelz wording (S5-P3), newest and more specific than the 4.1 wording."),
            b("It also exposes a risk-index + DNA-score, developed with feature ablation + error "
              "analysis.", ["L4.8@4.1"], "composed",
              "Phrases: 'risk-index + DNA-score'; 'feature ablation + error analysis' (ledger "
              "4.1, ForWheelz row)."),
        ],
        "capabilities": [
            b("Driver-risk intelligence", ["L4.8"]),
            b("28-feature trip pipeline from vehicle telemetry", ["L4.8"]),
            b("RF/XGBoost with ablation", ["L4.8"]),
            b("Output contracts", ["L4.8"]),
            b("Feature ablations and error analysis", ["S5-P3"]),
            b("Production-oriented outputs for confidence, risk contributors, and insurer/API "
              "integration", ["S5-P3"]),
            b("Risk-index + DNA-score", ["L4.8@4.1"]),
        ],
    },
    {
        "slug": "email-mcp",
        "name": b("email-MCP", ["L4.9"]),
        "one_liner": b("MCP tool server, 29 tests, documented.", ["L4.9"]),
        "group": 3,
        "featured": False,
        "tech_line": [b("MCP", ["L4.9"])],
        "overview": [
            b("An MCP tool server, documented, with 29 tests.", ["L4.9"], "composed",
              "Phrases: 'MCP tool server', '29 tests', 'documented' (L4.9). Page is short by "
              "design: no approved material adds depth beyond the ledger row (PRD: short is "
              "correct, padded is a defect)."),
        ],
        "capabilities": [
            b("MCP tool server", ["L4.9"]),
            b("29 tests", ["L4.9"]),
            b("Documented", ["L4.9"]),
        ],
    },
    {
        "slug": "voice-agent-core",
        "name": b("Voice agent core", ["L4.10"]),
        "one_liner": b("VAD→Whisper→LLM→TTS pipeline, Twilio-ready, Arabic + English.", ["L4.10"]),
        "group": 3,
        "featured": False,
        "tech_line": [
            b("VAD → Whisper → LLM → TTS", ["L4.10"]),
            b("Twilio", ["L4.10"]),
        ],
        "overview": [
            b("A voice agent pipeline: VAD → Whisper → LLM → TTS. It is Twilio-ready and covers "
              "Arabic + English.", ["L4.10"], "composed",
              "Phrases: 'VAD→Whisper→LLM→TTS pipeline', 'Twilio-ready', 'Arabic + English' "
              "(L4.10)."),
        ],
        "capabilities": [
            b("VAD → Whisper → LLM → TTS pipeline", ["L4.10"]),
            b("Twilio-ready", ["L4.10"]),
            b("Arabic + English", ["L4.10"]),
        ],
    },
]

PROJECT_ORDER = [p["slug"] for p in PROJECTS]
