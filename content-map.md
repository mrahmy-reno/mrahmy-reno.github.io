# content-map.md — provenance map for the Benchmark #1 portfolio

**Purpose.** Every factual claim rendered by the published site is listed here against the `FACTS_LEDGER.md` row that authorises it. This file is the audited artefact behind acceptance criterion **A1** (0 unsourced claims) and the PRD's rule **R4** (a rendered factual sentence that cannot be mapped is deleted, not reworded).

**Generated** by `python3 tools/gen_content_map.py` from `tools/site_content.py` — the same content model that renders `docs/`. Blocks rendered by the generator: **623**; distinct strings: **11** global + **440** page-specific.

### Ref scheme

| Ref | FACTS_LEDGER location | Notes |
|---|---|---|
| `L1.1` | §1 full name | |
| `L1.2` | §1 live LinkedIn headline | |
| `L1.4` | §1 location | |
| `L1.5` | §1 professional photo | Tier C — released by the owner (see switch log) |
| `L2.1` | §2 positioning statement (S3) | elisions resolved, composition exception E1 |
| `L2.2` | §2 resume summary (S2) | |
| `L3.1` | §3 role 1 (role, employer, dates) | employer name per `S5-R1` resolution |
| `L3.2` | §3 role 2 (role, employer, dates) | dates/employer per `S5-R3`/`S5-R4` |
| `L3.3` | §3 role 3 (retained per `S5-R5`) | |
| `L3.4` | §3 bullets block | |
| `L4.1`–`L4.10` | §4 project rows a–j | one row per project |
| `L4.x@4.1` | §4 **plus** the §4.1 approved extension row for that project | verbatim owner-authored specifics |
| `L5.1` | §5 skills block | |
| `L6.1`, `L6.2` | §6 education | |
| `L7.1`–`L7.5` | §7 Tier-A certifications | |
| `L7.6` | §7 Tier-B certifications | NOT rendered in the delivered build (0 occurrences) |
| `L8.1`, `L8.2` | §8 email / phone | NOT rendered (owner decision Q5 = LinkedIn only) |
| `L8.3` | §8 LinkedIn URL | the only external hyperlink destination |
| `S5-R1`…`S5-R10` | §11 binding conflict resolutions (S5 "Resume Pro" is authoritative) | current title, SEWS-E dates/employer, Cribl wording, summary, bullets |
| `S5-P1`…`S5-P6` | §11 "New publishable facts from S5" | Renosystems bullets, SEWS-E bullets, ForWheelz wording, cert dates, education dates, skills additions |
| *(none)* | declared `structural` | headings, labels, navigation and link text: asserts no fact about the person |

**Declared composition exceptions**

- **E1 (ledger `L2.1`, hero pitch).** The ledger records the positioning statement with two `…`
  elisions. They are rendered as `I've built` and `and I've shipped` — the words present at those
  exact positions in the source the ledger cites (S3). No other text is filled in. Declared in
  `evidence/B1-01/claim_map.md` and required to appear here.
- **Em-dash rule for elisions.** Where a §4.1 row itself contains an elision (the HalalBot row),
  the marker is rendered as an em dash and nothing else changes.
- **Tense unification (SEWS-E bullet 1).** The merged bullet uses `Implement …; produce …` over
  `L3.4` + `S5-P2` phrases. No noun, number or scope was added; only the verb form was unified.

**How this map is verified mechanically**

```bash
python3 tests/text_scans.py --text <evidence>/rendered-text
```

that checker re-derives the authorised string set from the content model, extracts the rendered
text of all 12 pages in a headless browser, and fails if any rendered line is not either a
substring of an authorised string or an assembly of authorised pieces joined by legitimate
separators. Current result: **0 unsourced lines of 632 checked**.


---

## 1. Global blocks (rendered identically on every page)

These appear in the header, navigation, contact block or footer of **all 12 pages** (the footer/contact markup is shared by design). They are listed once here; the mechanical checker applies them to every page.

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Mohammed Tawfiq Rahmy | `L1.1` | verbatim | Owner-approved likeness (ledger L1.5, Tier C released by the owner's decision). Alt text is the ledger name; self-hosted copy, never hot-linked. |
| 2 | (opens in a new tab) | *(structural)* | structural | Accessible-name suffix on every link that opens a new tab. |
| 3 | Skip to content | *(structural)* | structural |  |
| 4 | Mohammed Tawfiq Rahmy — Associate Solutions Engineer — AI / GenAI Solutions, Renosystems · https://www.linkedin.com/in/mohammed-rahmy | `L1.1`, `S5-R2`, `S5-R1`, `L8.3` | print | Print-only header line assembled from mapped blocks (A17: name, current role + employer and the LinkedIn URL readable on the first printed page). |
| 5 | Menu | *(structural)* | structural |  |
| 6 | LinkedIn | `L8.3` | structural | Link text is the platform name; href is the L8.3 URL. |
| 7 | Back to top | *(structural)* | structural |  |
| 8 | Every claim on this site is sourced. | *(structural)* | structural | Process statement about this site; true by construction (A1). |
| 9 | © Mohammed Tawfiq Rahmy | `L1.1` | structural | Name only; deliberately no year token (PRD 4.8). |
| 10 | Mohammed Tawfiq Rahmy · https://www.linkedin.com/in/mohammed-rahmy | `L1.1`, `L8.3` | print | Print-only header line on a non-index page: name + LinkedIn URL only, so no employer name appears next to a project description (D17). Uses the same mapped blocks as the index variant. |
| 11 | All work | *(structural)* | structural |  |

---

## 2. Page-specific blocks


### P1 — index (single-page pitch)

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Mohammed Tawfiq Rahmy | `L1.1` | verbatim |  |
| 2 | Solutions Engineer \| Mechatronics × AI Systems | `L1.2` | verbatim | The live LinkedIn headline (S1). R9: the hero headline stays this string even though S5 has a newer keyword line. |
| 3 | AI Solutions Engineer who ships production agentic systems. I've built multi-agent platforms for security operations and safety-first AI teammates with typed contracts, grounding, evaluation gates, and approval binding, and I've shipped independent products where coding agents wrote most of the code under my direction (65-test suites, signed APKs, live dashboards). Enterprise discipline + builder velocity. | `L2.1` | composed | L2.1 verbatim with the two ledger elisions resolved to the words present at those exact positions in the source the ledger cites (PRD E1: 'I've built' / 'and I've shipped'). No other text added. Declared composition exception E1. |
| 4 | Associate Solutions Engineer — AI / GenAI Solutions | `S5-R2` | verbatim |  |
| 5 | Renosystems | `L3.1`, `S5-R1` | verbatim |  |
| 6 | Mar 2026 – Present | `L3.1` | verbatim |  |
| 7 | New Cairo, Egypt | `L1.4` | verbatim |  |
| 8 | multi-agent orchestration, RAG, MCP tooling, evaluation harnesses, and safety guardrails | `L2.2` | verbatim |  |
| 9 | Arabic (native) · English (C1) · German (A2) | `L5.1` | verbatim |  |
| 10 | Current | *(structural)* | structural |  |
| 11 | Based in | *(structural)* | structural |  |
| 12 | Focus | *(structural)* | structural |  |
| 13 | Languages | *(structural)* | structural |  |
| 14 | See selected work | *(structural)* | structural |  |
| 15 | Connect on LinkedIn | `L8.3` | structural | Link text is a call to action; href is the L8.3 URL. |
| 16 | About | *(structural)* | structural |  |
| 17 | AI Solutions Engineer building agentic and generative AI systems for security, operations, and analytics. Hands-on with Amazon Bedrock, Strands Agents, multi-agent orchestration, RAG, MCP/tool integrations, LLM evaluation, guardrails, and full-stack AI delivery; backed by AWS Professional and Associate certifications. | `S5-R9` | verbatim | The S5 summary, rendered verbatim in About (resolution R9: S5 summary feeds the About/positioning). |
| 18 | AI Solutions Engineer building production agentic systems: multi-agent orchestration, RAG, MCP tooling, evaluation harnesses, and safety guardrails. Enterprise-grade grounding and test discipline from security-operations work; ships complete products (backend, UI, mobile) with AI coding agents. | `L2.2` | verbatim | L2.2 verbatim (retained: S5 does not contradict it, it describes the same work). |
| 19 | Architect and implement evidence-grounded multi-agent SOC workflows using Strands Agents, Amazon Bedrock, Splunk/MCP integrations, and SOAR playbooks, with typed contracts, quality guards, verdict generation, and controlled write-back. | `S5-P1` | verbatim | S5 Renosystems bullet 1 (FACTS_LEDGER section 11, S5-P1). Describes the work without naming any project (D17 attribution guard preserved). |
| 20 | Build brokered investigation systems that decompose tasks across specialist agents while enforcing scope, attribution, grounding, evidence-link integrity, replayable traces, and adversarial/compliance tests. | `S5-P1` | verbatim | S5 Renosystems bullet 2 (S5-P1). No project name asserted. |
| 21 | Develop AI copilots across Splunk, Axiom, and Dremio with schema-grounded query/SQL generation, validation, visualization, session memory, telemetry, and React/Vite interfaces. | `S5-P1` | verbatim | S5 Renosystems bullet 3 (S5-P1). No project name asserted. |
| 22 | Engineer and evaluate RAG/agent stacks using BM25 + ChromaDB hybrid retrieval, reciprocal-rank fusion, neural reranking, semantic caching, RAGAS, LLM-as-judge validation, approval boundaries, and automated E2E gates. | `S5-P1` | verbatim | S5 Renosystems bullet 4 (S5-P1). No project name asserted. |
| 23 | Implement wiring-harness engineering changes from OEM documentation (DCS/PPMR, ECR) for Toyota, Stellantis, and Ford; produce BOMs, man-hour reports, and splice diagrams with production traceability. | `L3.4`, `S5-P2` | composed | Phrases: 'harness design changes from OEM documentation (DCS/PPMR, ECR) for Toyota, Stellantis, and Ford' (L3.4); 'produced BOMs, man-hour reports, and splice diagrams with production traceability' (S5-P2). Tense unified; no new noun, number or scope added. |
| 24 | Coordinate design and production stakeholders to troubleshoot technical issues and validate updates against cost, quality, and manufacturability constraints. | `S5-P2` | verbatim | S5 SEWS-E bullet 2 (S5-P2). |
| 25 | Automotive Drawing Office Engineer | `L3.2` | verbatim |  |
| 26 | Sumitomo Electric Wiring Systems – Europe (SEWS-E), Cairo | `L3.2`, `S5-R4` | verbatim |  |
| 27 | May 2024 – Feb 2026 | `L3.2`, `S5-R3` | verbatim |  |
| 28 | Biocompatible magneto-sperm fabrication via electrospinning, and a 4-coil electromagnetic control system with closed-loop positioning (Arduino, OpenCV). | `L3.4` | verbatim | Retained per resolution R5: S5 omits this role for brevity, nothing contradicts it. |
| 29 | Nano-Robotics Researcher | `L3.3` | verbatim |  |
| 30 | MNR Lab (Cairo) | `L3.3` | verbatim |  |
| 31 | Jun 2022 – Sep 2022 | `L3.3` | verbatim |  |
| 32 | Experience | *(structural)* | structural |  |
| 33 | Featured | *(structural)* | structural |  |
| 34 | SAMA — Agentic SOC Triage & Response Automation | `L4.1` | verbatim |  |
| 35 | Multistage agentic triage workflow, grounding/evidence controls, typed contracts. | `L4.1` | verbatim |  |
| 36 | SmartOps SOC App | `L4.2` | verbatim |  |
| 37 | Brokered multi-agent investigation platform: task broker, domain analysts, evidence-linked findings, replayable traces. | `L4.2` | verbatim |  |
| 38 | Milo AI Employee | `L4.3` | verbatim |  |
| 39 | Safety-first agentic operations teammate over simulated Splunk/Cribl incidents; approval binding, authority boundaries, redaction, budget/time limits. | `L4.3` | verbatim |  |
| 40 | PulseSec | `L4.4` | verbatim |  |
| 41 | Multi-domain investigation copilot: domain-pack architecture, MCP connectors, schema-grounded query generation, React/Vite UI with agent-trace telemetry. | `L4.4` | verbatim |  |
| 42 | Security operations & agent safety | *(structural)* | structural |  |
| 43 | Tonsy-GPT | `L4.5` | verbatim |  |
| 44 | Self-hosted RAG assistant: hybrid BM25 + ChromaDB, RRF, neural reranking, semantic caching, FastAPI/SSE + Next.js. | `L4.5` | verbatim |  |
| 45 | Smart Care | `L4.6` | verbatim |  |
| 46 | Network-ops analytics copilot: intent → grounded SQL → stats → visualisation agents, Dremio, streaming React UI. | `L4.6` | verbatim |  |
| 47 | Applied RAG & analytics | *(structural)* | structural |  |
| 48 | HalalBot | `L4.7` | verbatim |  |
| 49 | Shipped WhatsApp ordering product (signed Android APK, owner dashboard, 65-test suite, Arabic/English parsing, live tunnel E2E). | `L4.7` | verbatim |  |
| 50 | ForWheelz | `L4.8` | verbatim |  |
| 51 | Driver-risk intelligence: 28-feature trip pipeline from vehicle telemetry, RF/XGBoost with ablation, output contracts. | `L4.8` | verbatim |  |
| 52 | email-MCP | `L4.9` | verbatim |  |
| 53 | MCP tool server, 29 tests, documented. | `L4.9` | verbatim |  |
| 54 | Voice agent core | `L4.10` | verbatim |  |
| 55 | VAD→Whisper→LLM→TTS pipeline, Twilio-ready, Arabic + English. | `L4.10` | verbatim |  |
| 56 | Shipped products & ML systems | *(structural)* | structural |  |
| 57 | Selected work | *(structural)* | structural |  |
| 58 | Ten projects: security-operations agents, applied RAG and analytics, and shipped products. | `L4.1`, `L4.2`, `L4.3`, `L4.4`, `L4.5`, `L4.6`, `L4.7`, `L4.8`, `L4.9`, `L4.10` | composed | Structural enumeration of the ten ledger project rows; 'ten' equals the rendered card count (checked by the coverage test). |
| 59 | multi-agent orchestration (Strands Agents) | `L5.1` | verbatim |  |
| 60 | Claude Code / coding-agent workflows | `L5.1` | verbatim |  |
| 61 | MCP servers | `L5.1` | verbatim |  |
| 62 | agent evals (LLM-as-judge, RAGAS, blind-vs-shown) | `L5.1` | verbatim |  |
| 63 | approval binding & safety boundaries | `L5.1` | verbatim |  |
| 64 | grounding/evidence controls | `L5.1` | verbatim |  |
| 65 | LangChain | `S5-P6` | verbatim |  |
| 66 | Agentic AI | *(structural)* | structural |  |
| 67 | ChromaDB | `L5.1` | verbatim |  |
| 68 | BM25 + reciprocal-rank fusion | `L5.1` | verbatim |  |
| 69 | RRF | `S5-P6` | verbatim |  |
| 70 | neural reranking | `L5.1` | verbatim |  |
| 71 | FAISS | `L5.1` | verbatim |  |
| 72 | semantic caching | `L5.1` | verbatim |  |
| 73 | RAG | *(structural)* | structural |  |
| 74 | Amazon Bedrock | `L5.1` | verbatim |  |
| 75 | Azure OpenAI | `L5.1` | verbatim |  |
| 76 | Gemini | `L5.1` | verbatim |  |
| 77 | OpenAI | `L5.1` | verbatim |  |
| 78 | DeepSeek | `L5.1` | verbatim |  |
| 79 | LLM platforms | *(structural)* | structural |  |
| 80 | Python (asyncio, FastAPI, SSE) | `L5.1` | verbatim |  |
| 81 | TypeScript | `L5.1` | verbatim |  |
| 82 | Splunk | `L5.1` | verbatim |  |
| 83 | Cribl | `L5.1` | verbatim |  |
| 84 | Elasticsearch | `L5.1` | verbatim |  |
| 85 | Dremio | `L5.1` | verbatim |  |
| 86 | Axiom | `S5-P6` | verbatim |  |
| 87 | Pydantic | `L5.1` | verbatim |  |
| 88 | SQL | `L5.1` | verbatim |  |
| 89 | SQLite | `S5-P6` | verbatim |  |
| 90 | REST APIs | `S5-P6` | verbatim |  |
| 91 | Docker | `L5.1` | verbatim |  |
| 92 | Backend & data | *(structural)* | structural |  |
| 93 | React/Vite | `L5.1` | verbatim |  |
| 94 | Vite | `S5-P6` | verbatim |  |
| 95 | Next.js | `L5.1` | verbatim |  |
| 96 | Android WebView packaging & signing | `L5.1` | verbatim |  |
| 97 | Frontend & mobile | *(structural)* | structural |  |
| 98 | scikit-learn | `L5.1` | verbatim |  |
| 99 | XGBoost | `L5.1` | verbatim |  |
| 100 | Random Forest | `S5-P6` | verbatim |  |
| 101 | SentenceTransformers | `S5-P6` | verbatim |  |
| 102 | OpenCV | `L5.1` | verbatim |  |
| 103 | feature engineering | `L5.1` | verbatim |  |
| 104 | ML/CV | *(structural)* | structural |  |
| 105 | WhatsApp Business Cloud API | `L5.1` | verbatim |  |
| 106 | Twilio voice pipelines | `L5.1` | verbatim |  |
| 107 | Git/GitHub | `L5.1` | verbatim |  |
| 108 | web scraping | `L5.1` | verbatim |  |
| 109 | Pytest | `S5-P6` | verbatim |  |
| 110 | Playwright | `S5-P6` | verbatim |  |
| 111 | Also | *(structural)* | structural |  |
| 112 | Arabic (native) | `L5.1` | verbatim |  |
| 113 | English (C1) | `L5.1` | verbatim |  |
| 114 | German (A2) | `L5.1` | verbatim |  |
| 115 | Skills | *(structural)* | structural |  |
| 116 | CND Digital IC Design Diploma | `L6.1` | verbatim |  |
| 117 | American University in Cairo | `L6.1` | verbatim |  |
| 118 | ASIC RTL-to-GDSII · Verilog/SystemVerilog · Synopsys | `L6.1` | verbatim |  |
| 119 | Sep 2023 – Aug 2024 | `S5-P5` | verbatim |  |
| 120 | BSc Mechatronics Engineering | `L6.2` | verbatim |  |
| 121 | German University in Cairo | `L6.2` | verbatim |  |
| 122 | Thesis: magneto-sperm fabrication & characterisation | `L6.2` | verbatim |  |
| 123 | Oct 2018 – Jun 2023 | `S5-P5` | verbatim |  |
| 124 | Jul 2026 | `S5-P4` | verbatim |  |
| 125 | AWS Certified Generative AI Developer – Professional (AIP-C01) | `L7.1` | verbatim |  |
| 126 | Amazon Web Services | `L7.1` | verbatim |  |
| 127 | May 2026 | `S5-P4` | verbatim |  |
| 128 | AWS Certified Machine Learning Engineer – Associate (MLA-C01) | `L7.2` | verbatim |  |
| 129 | Amazon Web Services | `L7.2` | verbatim |  |
| 130 | Apr 2026 | `S5-P4` | verbatim |  |
| 131 | AWS Certified Solutions Architect – Associate (SAA-C03) | `L7.3` | verbatim |  |
| 132 | Amazon Web Services | `L7.3` | verbatim |  |
| 133 | Jun 2026 | `S5-P4` | verbatim |  |
| 134 | Cribl Certified Admin – Stream | `L7.4`, `S5-R6` | verbatim |  |
| 135 | Cribl | `L7.4` | verbatim |  |
| 136 | Generative AI with AWS | `L7.5` | verbatim |  |
| 137 | Udacity | `L7.5` | verbatim |  |
| 138 | Education & certifications | *(structural)* | structural |  |
| 139 | Certifications | *(structural)* | structural |  |
| 140 | Contact | *(structural)* | structural |  |
| 141 | Connect with me on LinkedIn | `L8.3` | structural | Link text is a call to action; href is the L8.3 URL. |
| 142 | linkedin.com/in/mohammed-rahmy | `L8.3` | verbatim |  |
| 143 | This site links to LinkedIn only. | *(structural)* | structural | Statement about this site's configured state, not a claim about the person. |
| 144 | Mohammed Tawfiq Rahmy — AI Solutions Engineer | `L1.1`, `L3.1` | composed | Title composed from the ledger name (L1.1) and role (L3.1). |
| 145 | AI Solutions Engineer building agentic and generative AI systems for security, operations, and analytics. Hands-on with Amazon Bedrock, Strands Agents, multi-agent orchestration, RAG, MCP/tool integrations, LLM evaluation, guardrails, and full-stack AI delivery. | `S5-R9` | verbatim | The S5 summary (authoritative positioning per resolution R9); the closing clause 'backed by AWS Professional and Associate certifications' is rendered in the About section rather than the meta description. |
| 146 | Work | *(structural)* | structural |  |
| 147 | Education | *(structural)* | structural |  |

### P3 — 404 recovery page

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Page not found | *(structural)* | structural |  |
| 2 | The page you were looking for is not on this site. | *(structural)* | structural |  |
| 3 | Back to the home page | *(structural)* | structural |  |
| 4 | Connect with me on LinkedIn | `L8.3` | structural | Link text is a call to action; href is the L8.3 URL. |
| 5 | linkedin.com/in/mohammed-rahmy | `L8.3` | verbatim |  |
| 6 | This site links to LinkedIn only. | *(structural)* | structural | Statement about this site's configured state, not a claim about the person. |
| 7 | Page not found — Mohammed Tawfiq Rahmy | `L1.1` | composed | Composed from the structural string 'Page not found' and the ledger name. |
| 8 | About | *(structural)* | structural |  |
| 9 | Experience | *(structural)* | structural |  |
| 10 | Work | *(structural)* | structural |  |
| 11 | Skills | *(structural)* | structural |  |
| 12 | Education | *(structural)* | structural |  |
| 13 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/sama-soc-triage.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | An agentic triage and response automation system for security operations. It runs a multistage agentic triage workflow built on Strands Agents and Amazon Bedrock, with MCP connectors, typed contracts and grounding controls. | `L4.1`, `L3.4` | composed | Phrases: 'agentic ... Triage & Response Automation' (L4.1 row name), 'security operations' (L3.4), 'multistage agentic triage workflow' (L4.1), 'Strands Agents', 'Amazon Bedrock', 'MCP connectors', 'typed contracts', 'grounding controls' (L4.1/L3.4). Connective verbs only. |
| 2 | The workflow covers context construction, active investigation, threat modeling, quality guards, and verdict generation, and it was developed under evaluation gates: LLM-as-judge checks, RAGAS and blind-vs-shown evals, plus contract, adversarial and compliance test suites. | `L4.1@4.1`, `L3.4` | composed | Phrases: 'context construction, active investigation, threat modeling, quality guards, and verdict generation' (ledger 4.1, SAMA row), 'LLM-as-judge', 'RAGAS', 'blind-vs-shown', 'contract/adversarial/compliance suites' (L3.4). |
| 3 | Grounding/evidence controls keep its output traceable to its source. | `L4.1` | composed | Phrases: 'grounding/evidence controls' (L4.1). No claim about the client, its data, its environment or its outcomes (SAMA rule: mention depth, never internals). |
| 4 | Multistage agentic triage workflow | `L4.1` | verbatim |  |
| 5 | Multi-agent triage, investigation and response | `L3.4` | verbatim |  |
| 6 | Context construction, active investigation, threat modeling, quality guards, and verdict generation | `L4.1@4.1` | verbatim |  |
| 7 | Grounding and evidence controls | `L4.1` | verbatim |  |
| 8 | Typed contracts | `L4.1` | verbatim |  |
| 9 | Strands Agents and Amazon Bedrock | `L3.4` | verbatim |  |
| 10 | MCP connectors | `L3.4` | verbatim |  |
| 11 | LLM-as-judge checks, RAGAS, blind-vs-shown evals | `L3.4` | verbatim |  |
| 12 | Contract, adversarial and compliance test suites | `L3.4` | verbatim |  |
| 13 | Strands Agents | `L3.4` | verbatim |  |
| 14 | Amazon Bedrock | `L3.4` | verbatim |  |
| 15 | Technology | *(structural)* | structural |  |
| 16 | Next project | *(structural)* | structural |  |
| 17 | SmartOps SOC App | `L4.2` | verbatim |  |
| 18 | All work | *(structural)* | structural |  |
| 19 | SAMA — Agentic SOC Triage & Response Automation | `L4.1` | verbatim |  |
| 20 | Multistage agentic triage workflow, grounding/evidence controls, typed contracts. | `L4.1` | verbatim |  |
| 21 | Overview | *(structural)* | structural |  |
| 22 | Capabilities & practices | *(structural)* | structural |  |
| 23 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 24 | SAMA — Agentic SOC Triage & Response Automation — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 25 | About | *(structural)* | structural |  |
| 26 | Experience | *(structural)* | structural |  |
| 27 | Work | *(structural)* | structural |  |
| 28 | Skills | *(structural)* | structural |  |
| 29 | Education | *(structural)* | structural |  |
| 30 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/smartops-soc-app.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | A brokered multi-agent investigation platform. A task broker coordinates domain analysts, and findings are evidence-linked and carried in replayable traces. | `L4.2` | composed | Phrases: 'brokered multi-agent investigation platform', 'task broker', 'domain analysts', 'evidence-linked findings', 'replayable traces' (L4.2). |
| 2 | It supports hypothesis-blind analysis, replayable traces, and VirusTotal enrichment. | `L4.2@4.1` | composed | Phrases: 'hypothesis-blind analysis, replayable traces, and VirusTotal enrichment' (ledger 4.1, SmartOps row). |
| 3 | Brokered multi-agent investigation platform | `L4.2` | verbatim |  |
| 4 | Task broker | `L4.2` | verbatim |  |
| 5 | Domain analysts | `L4.2` | verbatim |  |
| 6 | Evidence-linked findings | `L4.2` | verbatim |  |
| 7 | Replayable traces | `L4.2` | verbatim |  |
| 8 | Hypothesis-blind analysis | `L4.2@4.1` | verbatim |  |
| 9 | VirusTotal enrichment | `L4.2@4.1` | verbatim |  |
| 10 | Previous project | *(structural)* | structural |  |
| 11 | SAMA — Agentic SOC Triage & Response Automation | `L4.1` | verbatim |  |
| 12 | Next project | *(structural)* | structural |  |
| 13 | Milo AI Employee | `L4.3` | verbatim |  |
| 14 | All work | *(structural)* | structural |  |
| 15 | SmartOps SOC App | `L4.2` | verbatim |  |
| 16 | Brokered multi-agent investigation platform: task broker, domain analysts, evidence-linked findings, replayable traces. | `L4.2` | verbatim |  |
| 17 | Overview | *(structural)* | structural |  |
| 18 | Capabilities & practices | *(structural)* | structural |  |
| 19 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 20 | SmartOps SOC App — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 21 | About | *(structural)* | structural |  |
| 22 | Experience | *(structural)* | structural |  |
| 23 | Work | *(structural)* | structural |  |
| 24 | Skills | *(structural)* | structural |  |
| 25 | Education | *(structural)* | structural |  |
| 26 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/milo-ai-employee.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | A safety-first agentic operations teammate that works over simulated Splunk and Cribl incidents. Actions carry approval binding and the agent operates inside authority boundaries with redaction and budget/time limits, so its autonomy is bounded by design rather than assumed. | `L4.3` | composed | Phrases: 'safety-first agentic operations teammate', 'simulated Splunk/Cribl incidents', 'approval binding', 'authority boundaries', 'redaction', 'budget/time limits' (L4.3). |
| 2 | Its actions are idempotent and reconciled, and it runs on versioned agent skills behind evaluation gates. | `L4.3@4.1` | composed | Phrases: 'idempotent actions and reconciliation'; 'versioned agent skills, evaluation gates' (ledger 4.1, Milo row). |
| 3 | Safety-first agentic operations teammate | `L4.3` | verbatim |  |
| 4 | Simulated Splunk and Cribl incidents | `L4.3` | verbatim |  |
| 5 | Approval binding | `L4.3` | verbatim |  |
| 6 | Authority boundaries | `L4.3` | verbatim |  |
| 7 | Redaction | `L4.3` | verbatim |  |
| 8 | Budget and time limits | `L4.3` | verbatim |  |
| 9 | Idempotent actions and reconciliation | `L4.3@4.1` | verbatim |  |
| 10 | Versioned agent skills, evaluation gates | `L4.3@4.1` | verbatim |  |
| 11 | Simulated Splunk | `L4.3` | verbatim |  |
| 12 | Cribl | `L4.3` | verbatim |  |
| 13 | Technology | *(structural)* | structural |  |
| 14 | Previous project | *(structural)* | structural |  |
| 15 | SmartOps SOC App | `L4.2` | verbatim |  |
| 16 | Next project | *(structural)* | structural |  |
| 17 | PulseSec | `L4.4` | verbatim |  |
| 18 | All work | *(structural)* | structural |  |
| 19 | Milo AI Employee | `L4.3` | verbatim |  |
| 20 | Safety-first agentic operations teammate over simulated Splunk/Cribl incidents; approval binding, authority boundaries, redaction, budget/time limits. | `L4.3` | verbatim |  |
| 21 | Overview | *(structural)* | structural |  |
| 22 | Capabilities & practices | *(structural)* | structural |  |
| 23 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 24 | Milo AI Employee — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 25 | About | *(structural)* | structural |  |
| 26 | Experience | *(structural)* | structural |  |
| 27 | Work | *(structural)* | structural |  |
| 28 | Skills | *(structural)* | structural |  |
| 29 | Education | *(structural)* | structural |  |
| 30 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/pulsesec.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | A multi-domain investigation copilot built on a domain-pack architecture, with MCP connectors and schema-grounded query generation. | `L4.4` | composed | Phrases: 'multi-domain investigation copilot', 'domain-pack architecture', 'MCP connectors', 'schema-grounded query generation' (L4.4). |
| 2 | It handles timeline/case handling under guardrails, and exposes a React/Vite UI with agent-trace telemetry. | `L4.4`, `L4.4@4.1` | composed | Phrases: 'timeline/case handling, guardrails' (ledger 4.1, PulseSec row); 'React/Vite UI with agent-trace telemetry' (L4.4). |
| 3 | Evaluation harnesses and E2E coverage target grounding, pack selection, and guardrails. | `L4.4@4.1` | composed | Phrases: 'evaluation harnesses and E2E coverage for grounding, pack selection, and guardrails' (ledger 4.1, PulseSec row). |
| 4 | Multi-domain investigation copilot | `L4.4` | verbatim |  |
| 5 | Domain-pack architecture | `L4.4` | verbatim |  |
| 6 | MCP connectors | `L4.4` | verbatim |  |
| 7 | Schema-grounded query generation | `L4.4` | verbatim |  |
| 8 | React/Vite UI with agent-trace telemetry | `L4.4` | verbatim |  |
| 9 | Timeline/case handling, guardrails | `L4.4@4.1` | verbatim |  |
| 10 | Evaluation harnesses and E2E coverage for grounding, pack selection, and guardrails | `L4.4@4.1` | verbatim |  |
| 11 | React/Vite | `L4.4` | verbatim |  |
| 12 | Technology | *(structural)* | structural |  |
| 13 | Previous project | *(structural)* | structural |  |
| 14 | Milo AI Employee | `L4.3` | verbatim |  |
| 15 | Next project | *(structural)* | structural |  |
| 16 | Tonsy-GPT | `L4.5` | verbatim |  |
| 17 | All work | *(structural)* | structural |  |
| 18 | PulseSec | `L4.4` | verbatim |  |
| 19 | Multi-domain investigation copilot: domain-pack architecture, MCP connectors, schema-grounded query generation, React/Vite UI with agent-trace telemetry. | `L4.4` | verbatim |  |
| 20 | Overview | *(structural)* | structural |  |
| 21 | Capabilities & practices | *(structural)* | structural |  |
| 22 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 23 | PulseSec — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 24 | About | *(structural)* | structural |  |
| 25 | Experience | *(structural)* | structural |  |
| 26 | Work | *(structural)* | structural |  |
| 27 | Skills | *(structural)* | structural |  |
| 28 | Education | *(structural)* | structural |  |
| 29 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/tonsy-gpt.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | A self-hosted RAG assistant. Retrieval is hybrid BM25 + ChromaDB with RRF (reciprocal-rank fusion), plus neural reranking and semantic caching, behind a FastAPI/SSE + Next.js stack. | `L4.5`, `L5.1` | composed | Phrases: 'self-hosted RAG assistant', 'hybrid BM25 + ChromaDB', 'RRF', 'neural reranking', 'semantic caching', 'FastAPI/SSE + Next.js' (L4.5). 'reciprocal-rank fusion' expands the acronym using the L5.1 skills wording, as PRD 4.5 permits. |
| 2 | Retrieval supports parent-setting expansion, and session state is carried by a FastAPI/SSE backend with session persistence. | `L4.5@4.1` | composed | Phrases: 'parent-setting expansion'; 'FastAPI/SSE backend with session persistence' (ledger 4.1, Tonsy-GPT row). |
| 3 | Self-hosted RAG assistant | `L4.5` | verbatim |  |
| 4 | Hybrid BM25 + ChromaDB | `L4.5` | verbatim |  |
| 5 | RRF retrieval fusion | `L4.5` | verbatim |  |
| 6 | Neural reranking | `L4.5` | verbatim |  |
| 7 | Semantic caching | `L4.5` | verbatim |  |
| 8 | FastAPI/SSE + Next.js | `L4.5` | verbatim |  |
| 9 | Parent-setting expansion | `L4.5@4.1` | verbatim |  |
| 10 | FastAPI/SSE backend with session persistence | `L4.5@4.1` | verbatim |  |
| 11 | BM25 | `L4.5` | verbatim |  |
| 12 | ChromaDB | `L4.5` | verbatim |  |
| 13 | FastAPI/SSE | `L4.5` | verbatim |  |
| 14 | Next.js | `L4.5` | verbatim |  |
| 15 | Technology | *(structural)* | structural |  |
| 16 | Previous project | *(structural)* | structural |  |
| 17 | PulseSec | `L4.4` | verbatim |  |
| 18 | Next project | *(structural)* | structural |  |
| 19 | Smart Care | `L4.6` | verbatim |  |
| 20 | All work | *(structural)* | structural |  |
| 21 | Tonsy-GPT | `L4.5` | verbatim |  |
| 22 | Self-hosted RAG assistant: hybrid BM25 + ChromaDB, RRF, neural reranking, semantic caching, FastAPI/SSE + Next.js. | `L4.5` | verbatim |  |
| 23 | Overview | *(structural)* | structural |  |
| 24 | Capabilities & practices | *(structural)* | structural |  |
| 25 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 26 | Tonsy-GPT — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 27 | About | *(structural)* | structural |  |
| 28 | Experience | *(structural)* | structural |  |
| 29 | Work | *(structural)* | structural |  |
| 30 | Skills | *(structural)* | structural |  |
| 31 | Education | *(structural)* | structural |  |
| 32 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/smart-care.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | A network-ops analytics copilot that chains intent → grounded SQL → stats → visualisation agents, on Dremio with a streaming React UI. | `L4.6` | composed | Phrases: 'network-ops analytics copilot', 'intent → grounded SQL → stats → visualisation agents', 'Dremio', 'streaming React UI' (L4.6). |
| 2 | An orchestrator with shared state, schema-aware prompting and session memory coordinates the chain. | `L4.6@4.1` | composed | Phrases: 'orchestrator + shared state, schema-aware prompting, session memory' (ledger 4.1, Smart Care row). |
| 3 | Network-ops analytics copilot | `L4.6` | verbatim |  |
| 4 | Intent → grounded SQL → stats → visualisation agents | `L4.6` | verbatim |  |
| 5 | Dremio | `L4.6` | verbatim |  |
| 6 | Streaming React UI | `L4.6` | verbatim |  |
| 7 | Orchestrator + shared state | `L4.6@4.1` | verbatim |  |
| 8 | Schema-aware prompting | `L4.6@4.1` | verbatim |  |
| 9 | Session memory | `L4.6@4.1` | verbatim |  |
| 10 | React | `L4.6` | verbatim |  |
| 11 | Technology | *(structural)* | structural |  |
| 12 | Previous project | *(structural)* | structural |  |
| 13 | Tonsy-GPT | `L4.5` | verbatim |  |
| 14 | Next project | *(structural)* | structural |  |
| 15 | HalalBot | `L4.7` | verbatim |  |
| 16 | All work | *(structural)* | structural |  |
| 17 | Smart Care | `L4.6` | verbatim |  |
| 18 | Network-ops analytics copilot: intent → grounded SQL → stats → visualisation agents, Dremio, streaming React UI. | `L4.6` | verbatim |  |
| 19 | Overview | *(structural)* | structural |  |
| 20 | Capabilities & practices | *(structural)* | structural |  |
| 21 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 22 | Smart Care — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 23 | About | *(structural)* | structural |  |
| 24 | Experience | *(structural)* | structural |  |
| 25 | Work | *(structural)* | structural |  |
| 26 | Skills | *(structural)* | structural |  |
| 27 | Education | *(structural)* | structural |  |
| 28 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/halalbot.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | A shipped WhatsApp ordering product with a signed Android APK, an owner dashboard and a 65-test suite. | `L4.7` | composed | Phrases: 'shipped WhatsApp ordering product', 'signed Android APK', 'owner dashboard', '65-test suite' (L4.7). |
| 2 | It runs Arabic/English parsing, the end-to-end path was validated over a live tunnel, and the stack spans Python/FastAPI, React and mobile packaging. | `L4.7`, `L3.4` | composed | Phrases: 'Arabic/English parsing', 'live tunnel E2E' (L4.7); 'Python/FastAPI, React, mobile packaging' (L3.4). |
| 3 | Two production bugs agents' own tests blessed — root-caused from live logs, pinned as regression tests. | `L4.7@4.1` | composed | Phrases: 'two production bugs agents' own tests blessed … root-caused from live logs, pinned as regression tests' (ledger 4.1, HalalBot row). The ledger's elision marker is rendered as an em dash and nothing else is changed. |
| 4 | Shipped WhatsApp ordering product | `L4.7` | verbatim |  |
| 5 | Signed Android APK | `L4.7` | verbatim |  |
| 6 | Owner dashboard | `L4.7` | verbatim |  |
| 7 | 65-test suite | `L4.7` | verbatim |  |
| 8 | Arabic/English parsing | `L4.7` | verbatim |  |
| 9 | Live tunnel E2E | `L4.7` | verbatim |  |
| 10 | Python/FastAPI, React, mobile packaging | `L3.4` | verbatim |  |
| 11 | Two production bugs agents' own tests blessed — root-caused from live logs, pinned as regression tests | `L4.7@4.1` | verbatim |  |
| 12 | WhatsApp | `L4.7` | verbatim |  |
| 13 | Android APK | `L4.7` | verbatim |  |
| 14 | Technology | *(structural)* | structural |  |
| 15 | Previous project | *(structural)* | structural |  |
| 16 | Smart Care | `L4.6` | verbatim |  |
| 17 | Next project | *(structural)* | structural |  |
| 18 | ForWheelz | `L4.8` | verbatim |  |
| 19 | All work | *(structural)* | structural |  |
| 20 | HalalBot | `L4.7` | verbatim |  |
| 21 | Shipped WhatsApp ordering product (signed Android APK, owner dashboard, 65-test suite, Arabic/English parsing, live tunnel E2E). | `L4.7` | verbatim |  |
| 22 | Overview | *(structural)* | structural |  |
| 23 | Capabilities & practices | *(structural)* | structural |  |
| 24 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 25 | HalalBot — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 26 | About | *(structural)* | structural |  |
| 27 | Experience | *(structural)* | structural |  |
| 28 | Work | *(structural)* | structural |  |
| 29 | Skills | *(structural)* | structural |  |
| 30 | Education | *(structural)* | structural |  |
| 31 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/forwheelz.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Driver-risk intelligence built on a 28-feature trip pipeline from vehicle telemetry, with RF/XGBoost with ablation and explicit output contracts. | `L4.8` | composed | Phrases: 'driver-risk intelligence', '28-feature trip pipeline from vehicle telemetry', 'RF/XGBoost with ablation', 'output contracts' (L4.8). |
| 2 | Random Forest/XGBoost models were evaluated through feature ablations and error analysis, and production-oriented outputs were defined for confidence, risk contributors, and insurer/API integration. | `S5-P3` | verbatim | S5 ForWheelz wording (S5-P3), newest and more specific than the 4.1 wording. |
| 3 | It also exposes a risk-index + DNA-score, developed with feature ablation + error analysis. | `L4.8@4.1` | composed | Phrases: 'risk-index + DNA-score'; 'feature ablation + error analysis' (ledger 4.1, ForWheelz row). |
| 4 | Driver-risk intelligence | `L4.8` | verbatim |  |
| 5 | 28-feature trip pipeline from vehicle telemetry | `L4.8` | verbatim |  |
| 6 | RF/XGBoost with ablation | `L4.8` | verbatim |  |
| 7 | Output contracts | `L4.8` | verbatim |  |
| 8 | Feature ablations and error analysis | `S5-P3` | verbatim |  |
| 9 | Production-oriented outputs for confidence, risk contributors, and insurer/API integration | `S5-P3` | verbatim |  |
| 10 | Risk-index + DNA-score | `L4.8@4.1` | verbatim |  |
| 11 | RF/XGBoost | `L4.8` | verbatim |  |
| 12 | Technology | *(structural)* | structural |  |
| 13 | Previous project | *(structural)* | structural |  |
| 14 | HalalBot | `L4.7` | verbatim |  |
| 15 | Next project | *(structural)* | structural |  |
| 16 | email-MCP | `L4.9` | verbatim |  |
| 17 | All work | *(structural)* | structural |  |
| 18 | ForWheelz | `L4.8` | verbatim |  |
| 19 | Driver-risk intelligence: 28-feature trip pipeline from vehicle telemetry, RF/XGBoost with ablation, output contracts. | `L4.8` | verbatim |  |
| 20 | Overview | *(structural)* | structural |  |
| 21 | Capabilities & practices | *(structural)* | structural |  |
| 22 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 23 | ForWheelz — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 24 | About | *(structural)* | structural |  |
| 25 | Experience | *(structural)* | structural |  |
| 26 | Work | *(structural)* | structural |  |
| 27 | Skills | *(structural)* | structural |  |
| 28 | Education | *(structural)* | structural |  |
| 29 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/email-mcp.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | An MCP tool server, documented, with 29 tests. | `L4.9` | composed | Phrases: 'MCP tool server', '29 tests', 'documented' (L4.9). Page is short by design: no approved material adds depth beyond the ledger row (PRD: short is correct, padded is a defect). |
| 2 | MCP tool server | `L4.9` | verbatim |  |
| 3 | 29 tests | `L4.9` | verbatim |  |
| 4 | Documented | `L4.9` | verbatim |  |
| 5 | MCP | `L4.9` | verbatim |  |
| 6 | Technology | *(structural)* | structural |  |
| 7 | Previous project | *(structural)* | structural |  |
| 8 | ForWheelz | `L4.8` | verbatim |  |
| 9 | Next project | *(structural)* | structural |  |
| 10 | Voice agent core | `L4.10` | verbatim |  |
| 11 | All work | *(structural)* | structural |  |
| 12 | email-MCP | `L4.9` | verbatim |  |
| 13 | MCP tool server, 29 tests, documented. | `L4.9` | verbatim |  |
| 14 | Overview | *(structural)* | structural |  |
| 15 | Capabilities & practices | *(structural)* | structural |  |
| 16 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 17 | email-MCP — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 18 | About | *(structural)* | structural |  |
| 19 | Experience | *(structural)* | structural |  |
| 20 | Work | *(structural)* | structural |  |
| 21 | Skills | *(structural)* | structural |  |
| 22 | Education | *(structural)* | structural |  |
| 23 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/voice-agent-core.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | A voice agent pipeline: VAD → Whisper → LLM → TTS. It is Twilio-ready and covers Arabic + English. | `L4.10` | composed | Phrases: 'VAD→Whisper→LLM→TTS pipeline', 'Twilio-ready', 'Arabic + English' (L4.10). |
| 2 | VAD → Whisper → LLM → TTS pipeline | `L4.10` | verbatim |  |
| 3 | Twilio-ready | `L4.10` | verbatim |  |
| 4 | Arabic + English | `L4.10` | verbatim |  |
| 5 | VAD → Whisper → LLM → TTS | `L4.10` | verbatim |  |
| 6 | Twilio | `L4.10` | verbatim |  |
| 7 | Technology | *(structural)* | structural |  |
| 8 | Previous project | *(structural)* | structural |  |
| 9 | email-MCP | `L4.9` | verbatim |  |
| 10 | All work | *(structural)* | structural |  |
| 11 | Voice agent core | `L4.10` | verbatim |  |
| 12 | VAD→Whisper→LLM→TTS pipeline, Twilio-ready, Arabic + English. | `L4.10` | verbatim |  |
| 13 | Overview | *(structural)* | structural |  |
| 14 | Capabilities & practices | *(structural)* | structural |  |
| 15 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 16 | Voice agent core — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 17 | About | *(structural)* | structural |  |
| 18 | Experience | *(structural)* | structural |  |
| 19 | Work | *(structural)* | structural |  |
| 20 | Skills | *(structural)* | structural |  |
| 21 | Education | *(structural)* | structural |  |
| 22 | Contact | *(structural)* | structural |  |

---

## 3. Coverage summary

- mapped factual blocks (with at least one ledger ref): **282**
- structural blocks (assert no fact about the person): **169**
- unsourced rendered lines found by the mechanical checker: **0**
- Tier-B/§9 content: **0 occurrences** (ledger §7 Tier-B names are not present anywhere in the repository)

Notes on the delivered state (owner decisions, `site.config.json`):

- contact = LinkedIn only (`L8.3`); `L8.1`/`L8.2` are **not rendered** and the switch that would render them is asserted in both states by `tests/switch_integrity.py`.
- photo = **included** (`L1.5`, Tier C released by the owner): `docs/assets/profile.jpg`, a self-hosted copy of `sources/linkedin_profile_photo_400.jpg` (sha256 `be1dc0c6…89be`), alt text = `L1.1`.
- Tier-B certifications = **none** (`L7.6` renders nowhere).

