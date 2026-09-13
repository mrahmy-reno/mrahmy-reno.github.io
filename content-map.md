# content-map.md — provenance map for the Benchmark #1 portfolio

**Purpose.** Every factual claim rendered by the published site is listed here against the `FACTS_LEDGER.md` row that authorises it. This file is the audited artefact behind acceptance criterion **A1** (0 unsourced claims) and the PRD's rule **R4** (a rendered factual sentence that cannot be mapped is deleted, not reworded).

**Generated** by `python3 tools/gen_content_map.py` from `tools/site_content.py` — the same content model that renders `docs/`. Blocks rendered by the generator: **926**; distinct strings: **11** global + **701** page-specific.

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

**B2-08 fact correction (the role, wherever it is a FIELD).** The formal current title is
`Associate Solutions Engineer — AI / GenAI Solutions` (`FACTS_LEDGER.md` §11 row **R2**, source
**S5**, which wins over the older `L3.1` wording "AI Solutions Engineer"). It is the value of every
role field: the at-a-glance register, the experience entry, the `Person.jobTitle` in the JSON-LD,
the page `<title>` and the print-only header line. The older variant is permitted **only** inside
owner-authored summary prose (`L2.1` / `L2.2` / `S5-R9`, rendered in the hero pitch and About),
where it is a sentence the owner wrote rather than an assertion of a role field.

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
separators. Current result: **0 unsourced lines of 988 checked** (evidence/B2-08,
`04_text_scans.txt`).


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
| 1 | Agentic systems are only useful if their answers can be checked: grounding/evidence controls, typed contracts, evaluation gates, approval binding, authority boundaries, evidence-linked findings, replayable traces, idempotent actions and reconciliation. | `L4.1`, `L4.2`, `L4.3`, `L3.4` | composed | PROOF_PLAN.md section 7's sanctioned construction, at the phrase level: the framing clause is PROOF_PLAN section 7's own sentence, and every substantive phrase after the colon is a ledger phrase ('grounding/evidence controls', 'typed contracts' L4.1; 'evidence-linked findings', 'replayable traces' L4.2; 'approval binding', 'authority boundaries', 'idempotent actions and reconciliation' L4.3; 'evaluation gates' L4.1@4.1). No new noun, technology, employer, date, client or metric enters the sentence. |
| 2 | Solutions Engineer \| Mechatronics × AI Systems | `L1.2` | verbatim | The live LinkedIn headline (S1). R9: the hero headline stays this string even though S5 has a newer keyword line. |
| 3 | Active | *(structural)* | structural | Signal label (DESIGN_LANGUAGE.md §3.6). Condition C1 ACTIVE: the current role is true now and was not true before. Label is a noun-of-state, not an encouragement (DNA §5.6). |
| 4 | Mohammed Tawfiq Rahmy | `L1.1` | verbatim |  |
| 5 | I build production agentic systems: | `L2.1`, `L3.4` | composed | ART_DIRECTION.md section 2, composition rule R2. Phrases: 'I build' (verb, free under R2) + 'production agentic systems' (L2.1, verbatim). No noun, technology, employer, date, client, metric or scope detail is added. |
| 6 | grounded, evaluated, approval-bound. | `L3.4`, `L4.1`, `L4.3` | composed | ART_DIRECTION.md section 2, R2. Phrases: 'grounding/evidence controls' and 'grounding controls' (L3.4 / L4.1) -> 'grounded'; 'evaluation-gated agent development' (L3.4) and 'evaluation gates' (L4.1) -> 'evaluated'; 'approval binding' (L4.3) -> 'approval-bound'. The claim is a compression of phrases the ledger already prints, not a new assertion. |
| 7 | Current role | *(structural)* | structural |  |
| 8 | Associate Solutions Engineer — AI / GenAI Solutions | `S5-R2` | verbatim | The formal current role title (FACTS_LEDGER.md §11 R2, source S5). Used wherever a role is asserted as a field. The older L3.1 token 'AI Solutions Engineer' is retained only inside owner-authored summary prose. |
| 9 | Employer | *(structural)* | structural |  |
| 10 | Renosystems | `L3.1`, `S5-R1` | verbatim |  |
| 11 | Since | *(structural)* | structural |  |
| 12 | Mar 2026 – Present | `L3.1` | verbatim |  |
| 13 | Based in | *(structural)* | structural |  |
| 14 | New Cairo, Egypt | `L1.4` | verbatim |  |
| 15 | Focus | *(structural)* | structural |  |
| 16 | multi-agent orchestration, RAG, MCP tooling, evaluation harnesses, and safety guardrails | `L2.2` | verbatim |  |
| 17 | Languages | *(structural)* | structural |  |
| 18 | Arabic (native) · English (C1) · German (A2) | `L5.1` | verbatim |  |
| 19 | See selected work | *(structural)* | structural |  |
| 20 | Connect on LinkedIn | `L8.3` | structural | Link text is a call to action; href is the L8.3 URL. |
| 21 | About | *(structural)* | structural |  |
| 22 | Why this work matters, in the terms the work itself uses. | *(structural)* | structural |  |
| 23 | AI Solutions Engineer building agentic and generative AI systems for security, operations, and analytics. Hands-on with Amazon Bedrock, Strands Agents, multi-agent orchestration, RAG, MCP/tool integrations, LLM evaluation, guardrails, and full-stack AI delivery; backed by AWS Professional and Associate certifications. | `S5-R9` | verbatim | The S5 summary, rendered verbatim in About (resolution R9: S5 summary feeds the About/positioning). |
| 24 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 25 | Architect and implement evidence-grounded multi-agent SOC workflows using Strands Agents, Amazon Bedrock, Splunk/MCP integrations, and SOAR playbooks, with typed contracts, quality guards, verdict generation, and controlled write-back. | `S5-P1` | verbatim | S5 Renosystems bullet 1 (FACTS_LEDGER section 11, S5-P1). Describes the work without naming any project (D17 attribution guard preserved). |
| 26 | Build brokered investigation systems that decompose tasks across specialist agents while enforcing scope, attribution, grounding, evidence-link integrity, replayable traces, and adversarial/compliance tests. | `S5-P1` | verbatim | S5 Renosystems bullet 2 (S5-P1). No project name asserted. |
| 27 | Develop AI copilots across Splunk, Axiom, and Dremio with schema-grounded query/SQL generation, validation, visualization, session memory, telemetry, and React/Vite interfaces. | `S5-P1` | verbatim | S5 Renosystems bullet 3 (S5-P1). No project name asserted. |
| 28 | Engineer and evaluate RAG/agent stacks using BM25 + ChromaDB hybrid retrieval, reciprocal-rank fusion, neural reranking, semantic caching, RAGAS, LLM-as-judge validation, approval boundaries, and automated E2E gates. | `S5-P1` | verbatim | S5 Renosystems bullet 4 (S5-P1). No project name asserted. |
| 29 | Present | *(structural)* | structural | Factual state marker on the current role (L3.1 dates). |
| 30 | Implement wiring-harness engineering changes from OEM documentation (DCS/PPMR, ECR) for Toyota, Stellantis, and Ford; produce BOMs, man-hour reports, and splice diagrams with production traceability. | `L3.4`, `S5-P2` | composed | Phrases: 'harness design changes from OEM documentation (DCS/PPMR, ECR) for Toyota, Stellantis, and Ford' (L3.4); 'produced BOMs, man-hour reports, and splice diagrams with production traceability' (S5-P2). Tense unified; no new noun, number or scope added. |
| 31 | Coordinate design and production stakeholders to troubleshoot technical issues and validate updates against cost, quality, and manufacturability constraints. | `S5-P2` | verbatim | S5 SEWS-E bullet 2 (S5-P2). |
| 32 | Automotive Drawing Office Engineer | `L3.2` | verbatim |  |
| 33 | Sumitomo Electric Wiring Systems – Europe (SEWS-E), Cairo | `L3.2`, `S5-R4` | verbatim |  |
| 34 | May 2024 – Feb 2026 | `L3.2`, `S5-R3` | verbatim |  |
| 35 | Biocompatible magneto-sperm fabrication via electrospinning, and a 4-coil electromagnetic control system with closed-loop positioning (Arduino, OpenCV). | `L3.4` | verbatim | Retained per resolution R5: S5 omits this role for brevity, nothing contradicts it. |
| 36 | Nano-Robotics Researcher | `L3.3` | verbatim |  |
| 37 | MNR Lab (Cairo) | `L3.3` | verbatim |  |
| 38 | Jun 2022 – Sep 2022 | `L3.3` | verbatim |  |
| 39 | Experience | *(structural)* | structural |  |
| 40 | Roles and dates, newest first. | *(structural)* | structural |  |
| 41 | Featured | *(structural)* | structural |  |
| 42 | Multistage agentic triage workflow, grounding/evidence controls, typed contracts. | `L4.1` | verbatim |  |
| 43 | 01 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 44 | SAMA — Agentic SOC Triage & Response Automation | `L4.1` | verbatim |  |
| 45 | Open | *(structural)* | structural | Link text on a project row; the accessible name also carries the project name. |
| 46 | Brokered multi-agent investigation platform: task broker, domain analysts, evidence-linked findings, replayable traces. | `L4.2` | verbatim |  |
| 47 | 02 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 48 | SmartOps SOC App | `L4.2` | verbatim |  |
| 49 | Safety-first agentic operations teammate over simulated Splunk/Cribl incidents; approval binding, authority boundaries, redaction, budget/time limits. | `L4.3` | verbatim |  |
| 50 | 03 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 51 | Milo AI Employee | `L4.3` | verbatim |  |
| 52 | Multi-domain investigation copilot: domain-pack architecture, MCP connectors, schema-grounded query generation, React/Vite UI with agent-trace telemetry. | `L4.4` | verbatim |  |
| 53 | 04 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 54 | PulseSec | `L4.4` | verbatim |  |
| 55 | Security operations & agent safety | *(structural)* | structural |  |
| 56 | 05 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 57 | Tonsy-GPT | `L4.5` | verbatim |  |
| 58 | 06 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 59 | Smart Care | `L4.6` | verbatim |  |
| 60 | Applied RAG & analytics | *(structural)* | structural |  |
| 61 | 07 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 62 | HalalBot | `L4.7` | verbatim |  |
| 63 | 08 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 64 | ForWheelz | `L4.8` | verbatim |  |
| 65 | 09 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 66 | email-MCP | `L4.9` | verbatim |  |
| 67 | 10 | *(structural)* | structural | Project catalogue position, in the ledger's own L4.1-L4.10 order. |
| 68 | Voice agent core | `L4.10` | verbatim |  |
| 69 | Shipped products & ML systems | *(structural)* | structural |  |
| 70 | Selected work | *(structural)* | structural |  |
| 71 | Ten projects across security-operations agents, applied RAG and analytics, and shipped products. | *(structural)* | structural | Structural deck: names the three groups that the rows themselves render. |
| 72 | Artefact | *(structural)* | structural |  |
| 73 | SAMA — one triage run: the ledger's five stages, controls across all of them, evaluation at the verdict. | `L4.1`, `L4.1@4.1` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 74 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 75 | SAMA — the verdict's contract, as a shape. | `L4.1` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 76 | Schematic — interface shape only. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 77 | Also drawn | *(structural)* | structural |  |
| 78 | All ten projects | *(structural)* | structural |  |
| 79 | Work, shown | *(structural)* | structural |  |
| 80 | How one of them runs: the stages, the controls bound across them, and the contract at the end. | *(structural)* | structural | Structural deck describing what the two objects below it draw. It no longer claims a map of the series (B2-04 / D3: the section used to draw the ten project names). |
| 81 | multi-agent orchestration (Strands Agents) | `L5.1` | verbatim |  |
| 82 | Claude Code / coding-agent workflows | `L5.1` | verbatim |  |
| 83 | MCP servers | `L5.1` | verbatim |  |
| 84 | agent evals (LLM-as-judge, RAGAS, blind-vs-shown) | `L5.1` | verbatim |  |
| 85 | approval binding & safety boundaries | `L5.1` | verbatim |  |
| 86 | grounding/evidence controls | `L5.1` | verbatim |  |
| 87 | LangChain | `S5-P6` | verbatim |  |
| 88 | Agentic AI | *(structural)* | structural |  |
| 89 | ChromaDB | `L5.1` | verbatim |  |
| 90 | BM25 + reciprocal-rank fusion | `L5.1` | verbatim |  |
| 91 | RRF | `S5-P6` | verbatim |  |
| 92 | neural reranking | `L5.1` | verbatim |  |
| 93 | FAISS | `L5.1` | verbatim |  |
| 94 | semantic caching | `L5.1` | verbatim |  |
| 95 | RAG | *(structural)* | structural |  |
| 96 | Amazon Bedrock | `L5.1` | verbatim |  |
| 97 | Azure OpenAI | `L5.1` | verbatim |  |
| 98 | Gemini | `L5.1` | verbatim |  |
| 99 | OpenAI | `L5.1` | verbatim |  |
| 100 | DeepSeek | `L5.1` | verbatim |  |
| 101 | LLM platforms | *(structural)* | structural |  |
| 102 | Python (asyncio, FastAPI, SSE) | `L5.1` | verbatim |  |
| 103 | TypeScript | `L5.1` | verbatim |  |
| 104 | Splunk | `L5.1` | verbatim |  |
| 105 | Cribl | `L5.1` | verbatim |  |
| 106 | Elasticsearch | `L5.1` | verbatim |  |
| 107 | Dremio | `L5.1` | verbatim |  |
| 108 | Axiom | `S5-P6` | verbatim |  |
| 109 | Pydantic | `L5.1` | verbatim |  |
| 110 | SQL | `L5.1` | verbatim |  |
| 111 | SQLite | `S5-P6` | verbatim |  |
| 112 | REST APIs | `S5-P6` | verbatim |  |
| 113 | Docker | `L5.1` | verbatim |  |
| 114 | Backend & data | *(structural)* | structural |  |
| 115 | React/Vite | `L5.1` | verbatim |  |
| 116 | Vite | `S5-P6` | verbatim |  |
| 117 | Next.js | `L5.1` | verbatim |  |
| 118 | Android WebView packaging & signing | `L5.1` | verbatim |  |
| 119 | Frontend & mobile | *(structural)* | structural |  |
| 120 | scikit-learn | `L5.1` | verbatim |  |
| 121 | XGBoost | `L5.1` | verbatim |  |
| 122 | Random Forest | `S5-P6` | verbatim |  |
| 123 | SentenceTransformers | `S5-P6` | verbatim |  |
| 124 | OpenCV | `L5.1` | verbatim |  |
| 125 | feature engineering | `L5.1` | verbatim |  |
| 126 | ML/CV | *(structural)* | structural |  |
| 127 | WhatsApp Business Cloud API | `L5.1` | verbatim |  |
| 128 | Twilio voice pipelines | `L5.1` | verbatim |  |
| 129 | Git/GitHub | `L5.1` | verbatim |  |
| 130 | web scraping | `L5.1` | verbatim |  |
| 131 | Pytest | `S5-P6` | verbatim |  |
| 132 | Playwright | `S5-P6` | verbatim |  |
| 133 | Also | *(structural)* | structural |  |
| 134 | Arabic (native) | `L5.1` | verbatim |  |
| 135 | English (C1) | `L5.1` | verbatim |  |
| 136 | German (A2) | `L5.1` | verbatim |  |
| 137 | Skills | *(structural)* | structural |  |
| 138 | The stack, grouped. Names are the ledger's own. | *(structural)* | structural |  |
| 139 | CND Digital IC Design Diploma | `L6.1` | verbatim |  |
| 140 | American University in Cairo | `L6.1` | verbatim |  |
| 141 | ASIC RTL-to-GDSII · Verilog/SystemVerilog · Synopsys | `L6.1` | verbatim |  |
| 142 | Sep 2023 – Aug 2024 | `S5-P5` | verbatim |  |
| 143 | BSc Mechatronics Engineering | `L6.2` | verbatim |  |
| 144 | German University in Cairo | `L6.2` | verbatim |  |
| 145 | Thesis: magneto-sperm fabrication & characterisation | `L6.2` | verbatim |  |
| 146 | Oct 2018 – Jun 2023 | `S5-P5` | verbatim |  |
| 147 | Jul 2026 | `S5-P4` | verbatim |  |
| 148 | AWS Certified Generative AI Developer – Professional (AIP-C01) | `L7.1` | verbatim |  |
| 149 | Amazon Web Services | `L7.1` | verbatim |  |
| 150 | May 2026 | `S5-P4` | verbatim |  |
| 151 | AWS Certified Machine Learning Engineer – Associate (MLA-C01) | `L7.2` | verbatim |  |
| 152 | Amazon Web Services | `L7.2` | verbatim |  |
| 153 | Apr 2026 | `S5-P4` | verbatim |  |
| 154 | AWS Certified Solutions Architect – Associate (SAA-C03) | `L7.3` | verbatim |  |
| 155 | Amazon Web Services | `L7.3` | verbatim |  |
| 156 | Jun 2026 | `S5-P4` | verbatim |  |
| 157 | Cribl Certified Admin – Stream | `L7.4`, `S5-R6` | verbatim |  |
| 158 | Cribl | `L7.4` | verbatim |  |
| 159 | Generative AI with AWS | `L7.5` | verbatim |  |
| 160 | Udacity | `L7.5` | verbatim |  |
| 161 | Education & certifications | *(structural)* | structural |  |
| 162 | Credentials and the bodies that issued them. | *(structural)* | structural |  |
| 163 | Certifications | *(structural)* | structural |  |
| 164 | Contact | *(structural)* | structural |  |
| 165 | One route, and it is LinkedIn. | *(structural)* | structural |  |
| 166 | Connect with me on LinkedIn | `L8.3` | structural | Link text is a call to action; href is the L8.3 URL. |
| 167 | linkedin.com/in/mohammed-rahmy | `L8.3` | verbatim |  |
| 168 | This site links to LinkedIn only. | *(structural)* | structural | Statement about this site's configured state, not a claim about the person. |
| 169 | Mohammed Tawfiq Rahmy — Associate Solutions Engineer — AI / GenAI Solutions | `L1.1`, `S5-R2` | composed | Title composed from the ledger name (L1.1) and the formal current role (FACTS_LEDGER §11 R2, source S5). The older L3.1 token 'AI Solutions Engineer' is not used as a title field; it survives only inside the owner-authored summary prose. |
| 170 | I build agentic and generative AI systems for security, operations, and analytics. Hands-on with Amazon Bedrock, Strands Agents, multi-agent orchestration, RAG, MCP/tool integrations, LLM evaluation, guardrails, and full-stack AI delivery. | `S5-R9` | composed | B2-04 / D11 repair: the S5 summary with its opening clause recast to a first-person, non-title phrase — 'I build …' replaces 'AI Solutions Engineer building …' — so that the meta description no longer repeats the job title beside the <title> field in a search result or link preview. Every substantive word after the opening clause is the S5 summary's own (the closing clause about certifications is rendered in About). No new fact is added. |
| 171 | Work | *(structural)* | structural |  |
| 172 | Education | *(structural)* | structural |  |

### P3 — 404 recovery page

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | SAMA — Agentic SOC Triage & Response Automation | `L4.1` | verbatim |  |
| 2 | SmartOps SOC App | `L4.2` | verbatim |  |
| 3 | Milo AI Employee | `L4.3` | verbatim |  |
| 4 | PulseSec | `L4.4` | verbatim |  |
| 5 | Tonsy-GPT | `L4.5` | verbatim |  |
| 6 | Smart Care | `L4.6` | verbatim |  |
| 7 | HalalBot | `L4.7` | verbatim |  |
| 8 | ForWheelz | `L4.8` | verbatim |  |
| 9 | email-MCP | `L4.9` | verbatim |  |
| 10 | Voice agent core | `L4.10` | verbatim |  |
| 11 | This path isn't here. | *(structural)* | structural |  |
| 12 | The page you were looking for is not on this site. | *(structural)* | structural |  |
| 13 | Back to the home page | *(structural)* | structural |  |
| 14 | Every published page, mapped. | *(structural)* | structural |  |
| 15 | Ten projects — how they fit together. | `L4.1`, `L4.2`, `L4.3`, `L4.4`, `L4.5`, `L4.6`, `L4.7`, `L4.8`, `L4.9`, `L4.10` | composed | Structural caption for the system map. The ten node labels are the ledger project names; the three group labels are the structural grouping. |
| 16 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption (PROOF_PLAN.md section 5 rule 9). |
| 17 | All ten projects | *(structural)* | structural |  |
| 18 | Connect with me on LinkedIn | `L8.3` | structural | Link text is a call to action; href is the L8.3 URL. |
| 19 | linkedin.com/in/mohammed-rahmy | `L8.3` | verbatim |  |
| 20 | This site links to LinkedIn only. | *(structural)* | structural | Statement about this site's configured state, not a claim about the person. |
| 21 | Page not found — Mohammed Tawfiq Rahmy | `L1.1` | composed | Composed from the structural string 'Page not found' and the ledger name. |
| 22 | About | *(structural)* | structural |  |
| 23 | Experience | *(structural)* | structural |  |
| 24 | Work | *(structural)* | structural |  |
| 25 | Skills | *(structural)* | structural |  |
| 26 | Education | *(structural)* | structural |  |
| 27 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/sama-soc-triage.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | SAMA — one triage run: the ledger's five stages, controls across all of them, evaluation at the verdict. | `L4.1` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | SAMA — the verdict's contract, as a shape. | `L4.1` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 4 | Schematic — interface shape only. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 5 | Multistage agentic triage workflow | `L4.1` | verbatim |  |
| 6 | Multi-agent triage, investigation and response | `L3.4` | verbatim |  |
| 7 | Context construction, active investigation, threat modeling, quality guards, and verdict generation | `L4.1@4.1` | verbatim |  |
| 8 | Grounding and evidence controls | `L4.1` | verbatim |  |
| 9 | Typed contracts | `L4.1` | verbatim |  |
| 10 | Strands Agents and Amazon Bedrock | `L3.4` | verbatim |  |
| 11 | MCP connectors | `L3.4` | verbatim |  |
| 12 | LLM-as-judge checks, RAGAS, blind-vs-shown evals | `L3.4` | verbatim |  |
| 13 | Contract, adversarial and compliance test suites | `L3.4` | verbatim |  |
| 14 | Scope | *(structural)* | structural |  |
| 15 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 16 | Strands Agents | `L3.4` | verbatim |  |
| 17 | Amazon Bedrock | `L3.4` | verbatim |  |
| 18 | Technology | *(structural)* | structural |  |
| 19 | Next project | *(structural)* | structural |  |
| 20 | SmartOps SOC App | `L4.2` | verbatim |  |
| 21 | An agentic triage and response automation system for security operations. It runs a multistage agentic triage workflow built on Strands Agents and Amazon Bedrock, with MCP connectors, typed contracts and grounding controls. | `L4.1`, `L3.4` | composed | Phrases: 'agentic ... Triage & Response Automation' (L4.1 row name), 'security operations' (L3.4), 'multistage agentic triage workflow' (L4.1), 'Strands Agents', 'Amazon Bedrock', 'MCP connectors', 'typed contracts', 'grounding controls' (L4.1/L3.4). Connective verbs only. |
| 22 | The workflow covers context construction, active investigation, threat modeling, quality guards, and verdict generation, and it was developed under evaluation gates: LLM-as-judge checks, RAGAS and blind-vs-shown evals, plus contract, adversarial and compliance test suites. | `L4.1@4.1`, `L3.4` | composed | Phrases: 'context construction, active investigation, threat modeling, quality guards, and verdict generation' (ledger 4.1, SAMA row), 'LLM-as-judge', 'RAGAS', 'blind-vs-shown', 'contract/adversarial/compliance suites' (L3.4). |
| 23 | Grounding/evidence controls keep its output traceable to its source. | `L4.1` | composed | Phrases: 'grounding/evidence controls' (L4.1). No claim about the client, its data, its environment or its outcomes (SAMA rule: mention depth, never internals). |
| 24 | All work | *(structural)* | structural |  |
| 25 | SAMA — Agentic SOC Triage & Response Automation | `L4.1` | verbatim |  |
| 26 | Multistage agentic triage workflow, grounding/evidence controls, typed contracts. | `L4.1` | verbatim |  |
| 27 | Security operations & agent safety | *(structural)* | structural |  |
| 28 | Overview | *(structural)* | structural |  |
| 29 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 30 | Problem | *(structural)* | structural |  |
| 31 | Security operations triage is the work: an agentic triage and response automation system runs a multistage agentic triage workflow. | `L4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 32 | Decision gate | *(structural)* | structural | Archetype label for the gate between two stages (A4 stage-gate). |
| 33 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 34 | Approach | *(structural)* | structural |  |
| 35 | Context construction, active investigation, threat modeling, quality guards, and verdict generation — with typed contracts and grounding controls around every stage. | `L4.1`, `L4.1@4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 36 | 03 / 06 | *(structural)* | structural | Case-study stage serial. |
| 37 | Architecture | *(structural)* | structural |  |
| 38 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 39 | The hard part | *(structural)* | structural |  |
| 40 | Grounding and evidence controls have to hold at every stage, so the output stays traceable to its source. | `L4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 41 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 42 | Evidence | *(structural)* | structural |  |
| 43 | Capabilities & practices | *(structural)* | structural |  |
| 44 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 45 | Outcome | *(structural)* | structural |  |
| 46 | Verdict generation at the end of an evaluation-gated workflow: LLM-as-judge checks, RAGAS and blind-vs-shown evals, plus contract, adversarial and compliance test suites. | `L4.1@4.1`, `L3.4` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 47 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 48 | SAMA — Agentic SOC Triage & Response Automation — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 49 | About | *(structural)* | structural |  |
| 50 | Experience | *(structural)* | structural |  |
| 51 | Work | *(structural)* | structural |  |
| 52 | Skills | *(structural)* | structural |  |
| 53 | Education | *(structural)* | structural |  |
| 54 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/smartops-soc-app.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | A brokered investigation run: broker, the analyst set, evidence-linked findings, trace lane. | `L4.2` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | The investigation record, as a shape. | `L4.2` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 4 | Schematic — interface shape only. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 5 | Brokered multi-agent investigation platform | `L4.2` | verbatim |  |
| 6 | Task broker | `L4.2` | verbatim |  |
| 7 | Domain analysts | `L4.2` | verbatim |  |
| 8 | Evidence-linked findings | `L4.2` | verbatim |  |
| 9 | Replayable traces | `L4.2` | verbatim |  |
| 10 | Hypothesis-blind analysis | `L4.2@4.1` | verbatim |  |
| 11 | VirusTotal enrichment | `L4.2@4.1` | verbatim |  |
| 12 | Scope | *(structural)* | structural |  |
| 13 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 14 | Previous project | *(structural)* | structural |  |
| 15 | SAMA — Agentic SOC Triage & Response Automation | `L4.1` | verbatim |  |
| 16 | Next project | *(structural)* | structural |  |
| 17 | Milo AI Employee | `L4.3` | verbatim |  |
| 18 | 03 / 06 | *(structural)* | structural | Case-study stage serial. |
| 19 | Architecture | *(structural)* | structural |  |
| 20 | The system | *(structural)* | structural | Archetype label for the hub plane (A3 hub/broker). Names the centre of the drawing. |
| 21 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 22 | Problem | *(structural)* | structural |  |
| 23 | Investigation has to be brokered: a task broker coordinates domain analysts. | `L4.2` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 24 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 25 | Approach | *(structural)* | structural |  |
| 26 | Findings are evidence-linked and carried in replayable traces, with hypothesis-blind analysis and VirusTotal enrichment. | `L4.2`, `L4.2@4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 27 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 28 | The hard part | *(structural)* | structural |  |
| 29 | Hypothesis-blind analysis across domain analysts, with findings that stay evidence-linked. | `L4.2`, `L4.2@4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 30 | A brokered multi-agent investigation platform. A task broker coordinates domain analysts, and findings are evidence-linked and carried in replayable traces. | `L4.2` | composed | Phrases: 'brokered multi-agent investigation platform', 'task broker', 'domain analysts', 'evidence-linked findings', 'replayable traces' (L4.2). |
| 31 | It supports hypothesis-blind analysis, replayable traces, and VirusTotal enrichment. | `L4.2@4.1` | composed | Phrases: 'hypothesis-blind analysis, replayable traces, and VirusTotal enrichment' (ledger 4.1, SmartOps row). |
| 32 | All work | *(structural)* | structural |  |
| 33 | SmartOps SOC App | `L4.2` | verbatim |  |
| 34 | Brokered multi-agent investigation platform: task broker, domain analysts, evidence-linked findings, replayable traces. | `L4.2` | verbatim |  |
| 35 | Security operations & agent safety | *(structural)* | structural |  |
| 36 | Overview | *(structural)* | structural |  |
| 37 | The parts | *(structural)* | structural | Archetype label for the bounded spokes around the hub. |
| 38 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 39 | Evidence | *(structural)* | structural |  |
| 40 | Capabilities & practices | *(structural)* | structural |  |
| 41 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 42 | Outcome | *(structural)* | structural |  |
| 43 | A brokered multi-agent investigation platform whose traces can be replayed. | `L4.2` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 44 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 45 | SmartOps SOC App — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 46 | About | *(structural)* | structural |  |
| 47 | Experience | *(structural)* | structural |  |
| 48 | Work | *(structural)* | structural |  |
| 49 | Skills | *(structural)* | structural |  |
| 50 | Education | *(structural)* | structural |  |
| 51 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/milo-ai-employee.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Approval binding and the authority boundary, on one request path. | `L4.3` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | The approval record, as a shape. | `L4.3` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 4 | Schematic — interface shape only. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 5 | Safety-first agentic operations teammate | `L4.3` | verbatim |  |
| 6 | Simulated Splunk and Cribl incidents | `L4.3` | verbatim |  |
| 7 | Approval binding | `L4.3` | verbatim |  |
| 8 | Authority boundaries | `L4.3` | verbatim |  |
| 9 | Redaction | `L4.3` | verbatim |  |
| 10 | Budget and time limits | `L4.3` | verbatim |  |
| 11 | Idempotent actions and reconciliation | `L4.3@4.1` | verbatim |  |
| 12 | Versioned agent skills, evaluation gates | `L4.3@4.1` | verbatim |  |
| 13 | Scope | *(structural)* | structural |  |
| 14 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 15 | Simulated Splunk | `L4.3` | verbatim |  |
| 16 | Cribl | `L4.3` | verbatim |  |
| 17 | Technology | *(structural)* | structural |  |
| 18 | Previous project | *(structural)* | structural |  |
| 19 | SmartOps SOC App | `L4.2` | verbatim |  |
| 20 | Next project | *(structural)* | structural |  |
| 21 | PulseSec | `L4.4` | verbatim |  |
| 22 | The drawing | *(structural)* | structural | Archetype label for the plate (A6 plate). |
| 23 | What it is | *(structural)* | structural | Archetype label for the closing human plane (the T2 close). |
| 24 | Safety-first agentic operations teammate over simulated Splunk/Cribl incidents; approval binding, authority boundaries, redaction, budget/time limits. | `L4.3` | verbatim |  |
| 25 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 26 | Outcome | *(structural)* | structural |  |
| 27 | A safety-first agentic operations teammate over simulated Splunk/Cribl incidents. | `L4.3` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 28 | A safety-first agentic operations teammate that works over simulated Splunk and Cribl incidents. Actions carry approval binding and the agent operates inside authority boundaries with redaction and budget/time limits, so its autonomy is bounded by design rather than assumed. | `L4.3` | composed | Phrases: 'safety-first agentic operations teammate', 'simulated Splunk/Cribl incidents', 'approval binding', 'authority boundaries', 'redaction', 'budget/time limits' (L4.3). |
| 29 | Its actions are idempotent and reconciled, and it runs on versioned agent skills behind evaluation gates. | `L4.3@4.1` | composed | Phrases: 'idempotent actions and reconciliation'; 'versioned agent skills, evaluation gates' (ledger 4.1, Milo row). |
| 30 | All work | *(structural)* | structural |  |
| 31 | Milo AI Employee | `L4.3` | verbatim |  |
| 32 | Security operations & agent safety | *(structural)* | structural |  |
| 33 | Overview | *(structural)* | structural |  |
| 34 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 35 | Problem | *(structural)* | structural |  |
| 36 | An operations teammate acts, so its autonomy has to be bounded by design rather than assumed. | `L4.3` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 37 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 38 | Approach | *(structural)* | structural |  |
| 39 | Approval binding, authority boundaries, redaction and budget/time limits bound every action; the incidents are simulated Splunk/Cribl. | `L4.3` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 40 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 41 | The hard part | *(structural)* | structural |  |
| 42 | Actions are idempotent and reconciled, and the agent skills are versioned behind evaluation gates. | `L4.3@4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 43 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 44 | Evidence | *(structural)* | structural |  |
| 45 | Capabilities & practices | *(structural)* | structural |  |
| 46 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 47 | Milo AI Employee — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 48 | About | *(structural)* | structural |  |
| 49 | Experience | *(structural)* | structural |  |
| 50 | Work | *(structural)* | structural |  |
| 51 | Skills | *(structural)* | structural |  |
| 52 | Education | *(structural)* | structural |  |
| 53 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/pulsesec.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Domain packs, connectors, grounded queries and the trace lane. | `L4.4` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | The domain pack, as a shape. | `L4.4` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 4 | Schematic — interface shape only. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 5 | Multi-domain investigation copilot | `L4.4` | verbatim |  |
| 6 | Domain-pack architecture | `L4.4` | verbatim |  |
| 7 | MCP connectors | `L4.4` | verbatim |  |
| 8 | Schema-grounded query generation | `L4.4` | verbatim |  |
| 9 | React/Vite UI with agent-trace telemetry | `L4.4` | verbatim |  |
| 10 | Timeline/case handling, guardrails | `L4.4@4.1` | verbatim |  |
| 11 | Evaluation harnesses and E2E coverage for grounding, pack selection, and guardrails | `L4.4@4.1` | verbatim |  |
| 12 | Scope | *(structural)* | structural |  |
| 13 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 14 | React/Vite | `L4.4` | verbatim |  |
| 15 | Technology | *(structural)* | structural |  |
| 16 | Previous project | *(structural)* | structural |  |
| 17 | Milo AI Employee | `L4.3` | verbatim |  |
| 18 | Next project | *(structural)* | structural |  |
| 19 | Tonsy-GPT | `L4.5` | verbatim |  |
| 20 | One copilot has to serve several domains without one domain's schema leaking into another's. | `L4.4` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 21 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 22 | Problem | *(structural)* | structural |  |
| 23 | A domain-pack architecture with MCP connectors and schema-grounded query generation, handling timelines and cases under guardrails. | `L4.4` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 24 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 25 | Approach | *(structural)* | structural |  |
| 26 | 03 / 06 | *(structural)* | structural | Case-study stage serial. |
| 27 | Architecture | *(structural)* | structural |  |
| 28 | Evaluation harnesses and E2E coverage target grounding, pack selection, and guardrails. | `L4.4@4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 29 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 30 | The hard part | *(structural)* | structural |  |
| 31 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 32 | Evidence | *(structural)* | structural |  |
| 33 | A multi-domain investigation copilot with a React/Vite UI and agent-trace telemetry. | `L4.4` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 34 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 35 | Outcome | *(structural)* | structural |  |
| 36 | A multi-domain investigation copilot built on a domain-pack architecture, with MCP connectors and schema-grounded query generation. | `L4.4` | composed | Phrases: 'multi-domain investigation copilot', 'domain-pack architecture', 'MCP connectors', 'schema-grounded query generation' (L4.4). |
| 37 | It handles timeline/case handling under guardrails, and exposes a React/Vite UI with agent-trace telemetry. | `L4.4`, `L4.4@4.1` | composed | Phrases: 'timeline/case handling, guardrails' (ledger 4.1, PulseSec row); 'React/Vite UI with agent-trace telemetry' (L4.4). |
| 38 | All work | *(structural)* | structural |  |
| 39 | PulseSec | `L4.4` | verbatim |  |
| 40 | Multi-domain investigation copilot: domain-pack architecture, MCP connectors, schema-grounded query generation, React/Vite UI with agent-trace telemetry. | `L4.4` | verbatim |  |
| 41 | Security operations & agent safety | *(structural)* | structural |  |
| 42 | Overview | *(structural)* | structural |  |
| 43 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 44 | PulseSec — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 45 | About | *(structural)* | structural |  |
| 46 | Experience | *(structural)* | structural |  |
| 47 | Work | *(structural)* | structural |  |
| 48 | Skills | *(structural)* | structural |  |
| 49 | Education | *(structural)* | structural |  |
| 50 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/tonsy-gpt.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Hybrid retrieval: fan-out, fusion, reranking, caching. | `L4.5` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | Self-hosted RAG assistant | `L4.5` | verbatim |  |
| 4 | Hybrid BM25 + ChromaDB | `L4.5` | verbatim |  |
| 5 | RRF retrieval fusion | `L4.5` | verbatim |  |
| 6 | Neural reranking | `L4.5` | verbatim |  |
| 7 | Semantic caching | `L4.5` | verbatim |  |
| 8 | FastAPI/SSE + Next.js | `L4.5` | verbatim |  |
| 9 | Parent-setting expansion | `L4.5@4.1` | verbatim |  |
| 10 | FastAPI/SSE backend with session persistence | `L4.5@4.1` | verbatim |  |
| 11 | Scope | *(structural)* | structural |  |
| 12 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 13 | BM25 | `L4.5` | verbatim |  |
| 14 | ChromaDB | `L4.5` | verbatim |  |
| 15 | FastAPI/SSE | `L4.5` | verbatim |  |
| 16 | Next.js | `L4.5` | verbatim |  |
| 17 | Technology | *(structural)* | structural |  |
| 18 | Previous project | *(structural)* | structural |  |
| 19 | PulseSec | `L4.4` | verbatim |  |
| 20 | Next project | *(structural)* | structural |  |
| 21 | Smart Care | `L4.6` | verbatim |  |
| 22 | A self-hosted RAG assistant. Retrieval is hybrid BM25 + ChromaDB with RRF (reciprocal-rank fusion), plus neural reranking and semantic caching, behind a FastAPI/SSE + Next.js stack. | `L4.5`, `L5.1` | composed | Phrases: 'self-hosted RAG assistant', 'hybrid BM25 + ChromaDB', 'RRF', 'neural reranking', 'semantic caching', 'FastAPI/SSE + Next.js' (L4.5). 'reciprocal-rank fusion' expands the acronym using the L5.1 skills wording, as PRD 4.5 permits. |
| 23 | Retrieval supports parent-setting expansion, and session state is carried by a FastAPI/SSE backend with session persistence. | `L4.5@4.1` | composed | Phrases: 'parent-setting expansion'; 'FastAPI/SSE backend with session persistence' (ledger 4.1, Tonsy-GPT row). |
| 24 | All work | *(structural)* | structural |  |
| 25 | Tonsy-GPT | `L4.5` | verbatim |  |
| 26 | Self-hosted RAG assistant: hybrid BM25 + ChromaDB, RRF, neural reranking, semantic caching, FastAPI/SSE + Next.js. | `L4.5` | verbatim |  |
| 27 | Applied RAG & analytics | *(structural)* | structural |  |
| 28 | Overview | *(structural)* | structural |  |
| 29 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 30 | Problem | *(structural)* | structural |  |
| 31 | Retrieval quality is the product: one retriever is not enough, and the assistant is self-hosted. | `L4.5` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 32 | Decision gate | *(structural)* | structural | Archetype label for the gate between two stages (A4 stage-gate). |
| 33 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 34 | Approach | *(structural)* | structural |  |
| 35 | Hybrid BM25 + ChromaDB retrieval, RRF (reciprocal-rank fusion), neural reranking and semantic caching, behind FastAPI/SSE and Next.js. | `L4.5`, `L5.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 36 | 03 / 06 | *(structural)* | structural | Case-study stage serial. |
| 37 | Architecture | *(structural)* | structural |  |
| 38 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 39 | The hard part | *(structural)* | structural |  |
| 40 | Parent-setting expansion and session state, carried by a FastAPI/SSE backend with session persistence. | `L4.5@4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 41 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 42 | Evidence | *(structural)* | structural |  |
| 43 | Capabilities & practices | *(structural)* | structural |  |
| 44 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 45 | Outcome | *(structural)* | structural |  |
| 46 | A self-hosted RAG assistant. | `L4.5` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 47 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 48 | Tonsy-GPT — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 49 | About | *(structural)* | structural |  |
| 50 | Experience | *(structural)* | structural |  |
| 51 | Work | *(structural)* | structural |  |
| 52 | Skills | *(structural)* | structural |  |
| 53 | Education | *(structural)* | structural |  |
| 54 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/smart-care.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Intent to grounded output. | `L4.6` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | Network-ops analytics copilot | `L4.6` | verbatim |  |
| 4 | Intent → grounded SQL → stats → visualisation agents | `L4.6` | verbatim |  |
| 5 | Dremio | `L4.6` | verbatim |  |
| 6 | Streaming React UI | `L4.6` | verbatim |  |
| 7 | Orchestrator + shared state | `L4.6@4.1` | verbatim |  |
| 8 | Schema-aware prompting | `L4.6@4.1` | verbatim |  |
| 9 | Session memory | `L4.6@4.1` | verbatim |  |
| 10 | Scope | *(structural)* | structural |  |
| 11 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 12 | React | `L4.6` | verbatim |  |
| 13 | Technology | *(structural)* | structural |  |
| 14 | Previous project | *(structural)* | structural |  |
| 15 | Tonsy-GPT | `L4.5` | verbatim |  |
| 16 | Next project | *(structural)* | structural |  |
| 17 | HalalBot | `L4.7` | verbatim |  |
| 18 | 03 / 06 | *(structural)* | structural | Case-study stage serial. |
| 19 | Architecture | *(structural)* | structural |  |
| 20 | The system | *(structural)* | structural | Archetype label for the hub plane (A3 hub/broker). Names the centre of the drawing. |
| 21 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 22 | Problem | *(structural)* | structural |  |
| 23 | Analytics questions arrive in intent, not SQL, and the answer has to be grounded. | `L4.6` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 24 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 25 | Approach | *(structural)* | structural |  |
| 26 | Intent → grounded SQL → stats → visualisation agents, on Dremio with a streaming React UI. | `L4.6` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 27 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 28 | The hard part | *(structural)* | structural |  |
| 29 | An orchestrator with shared state, schema-aware prompting and session memory coordinates the chain. | `L4.6@4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 30 | A network-ops analytics copilot that chains intent → grounded SQL → stats → visualisation agents, on Dremio with a streaming React UI. | `L4.6` | composed | Phrases: 'network-ops analytics copilot', 'intent → grounded SQL → stats → visualisation agents', 'Dremio', 'streaming React UI' (L4.6). |
| 31 | All work | *(structural)* | structural |  |
| 32 | Smart Care | `L4.6` | verbatim |  |
| 33 | Network-ops analytics copilot: intent → grounded SQL → stats → visualisation agents, Dremio, streaming React UI. | `L4.6` | verbatim |  |
| 34 | Applied RAG & analytics | *(structural)* | structural |  |
| 35 | Overview | *(structural)* | structural |  |
| 36 | The parts | *(structural)* | structural | Archetype label for the bounded spokes around the hub. |
| 37 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 38 | Evidence | *(structural)* | structural |  |
| 39 | Capabilities & practices | *(structural)* | structural |  |
| 40 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 41 | Outcome | *(structural)* | structural |  |
| 42 | A network-ops analytics copilot. | `L4.6` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 43 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 44 | Smart Care — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 45 | About | *(structural)* | structural |  |
| 46 | Experience | *(structural)* | structural |  |
| 47 | Work | *(structural)* | structural |  |
| 48 | Skills | *(structural)* | structural |  |
| 49 | Education | *(structural)* | structural |  |
| 50 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/halalbot.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Shipped surfaces: conversation, operations, release path. | `L4.7` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic wireframe shapes — not screenshots. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | Shipped WhatsApp ordering product | `L4.7` | verbatim |  |
| 4 | Signed Android APK | `L4.7` | verbatim |  |
| 5 | Owner dashboard | `L4.7` | verbatim |  |
| 6 | 65-test suite | `L4.7` | verbatim |  |
| 7 | Arabic/English parsing | `L4.7` | verbatim |  |
| 8 | Live tunnel E2E | `L4.7` | verbatim |  |
| 9 | Python/FastAPI, React, mobile packaging | `L3.4` | verbatim |  |
| 10 | Two production bugs agents' own tests blessed — root-caused from live logs, pinned as regression tests | `L4.7@4.1` | verbatim |  |
| 11 | Scope | *(structural)* | structural |  |
| 12 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 13 | WhatsApp | `L4.7` | verbatim |  |
| 14 | Android APK | `L4.7` | verbatim |  |
| 15 | Technology | *(structural)* | structural |  |
| 16 | Previous project | *(structural)* | structural |  |
| 17 | Smart Care | `L4.6` | verbatim |  |
| 18 | Next project | *(structural)* | structural |  |
| 19 | ForWheelz | `L4.8` | verbatim |  |
| 20 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 21 | Problem | *(structural)* | structural |  |
| 22 | Ordering happens in WhatsApp, and the product has to ship to a phone. | `L4.7` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 23 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 24 | Approach | *(structural)* | structural |  |
| 25 | A shipped WhatsApp ordering product with a signed Android APK, an owner dashboard and Arabic/English parsing, validated over a live tunnel. | `L4.7` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 26 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 27 | The hard part | *(structural)* | structural |  |
| 28 | Two production bugs agents' own tests blessed — root-caused from live logs, pinned as regression tests. | `L4.7@4.1` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 29 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 30 | Evidence | *(structural)* | structural |  |
| 31 | Capabilities & practices | *(structural)* | structural |  |
| 32 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 33 | Outcome | *(structural)* | structural |  |
| 34 | A shipped product: signed Android APK, owner dashboard, 65-test suite. | `L4.7` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 35 | Notes | *(structural)* | structural | Archetype label for the margin column (A8 marginalia). |
| 36 | 03 / 06 | *(structural)* | structural | Case-study stage serial. |
| 37 | Architecture | *(structural)* | structural |  |
| 38 | A shipped WhatsApp ordering product with a signed Android APK, an owner dashboard and a 65-test suite. | `L4.7` | composed | Phrases: 'shipped WhatsApp ordering product', 'signed Android APK', 'owner dashboard', '65-test suite' (L4.7). |
| 39 | It runs Arabic/English parsing, the end-to-end path was validated over a live tunnel, and the stack spans Python/FastAPI, React and mobile packaging. | `L4.7`, `L3.4` | composed | Phrases: 'Arabic/English parsing', 'live tunnel E2E' (L4.7); 'Python/FastAPI, React, mobile packaging' (L3.4). |
| 40 | All work | *(structural)* | structural |  |
| 41 | HalalBot | `L4.7` | verbatim |  |
| 42 | Shipped WhatsApp ordering product (signed Android APK, owner dashboard, 65-test suite, Arabic/English parsing, live tunnel E2E). | `L4.7` | verbatim |  |
| 43 | Shipped products & ML systems | *(structural)* | structural |  |
| 44 | Overview | *(structural)* | structural |  |
| 45 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 46 | HalalBot — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 47 | About | *(structural)* | structural |  |
| 48 | Experience | *(structural)* | structural |  |
| 49 | Work | *(structural)* | structural |  |
| 50 | Skills | *(structural)* | structural |  |
| 51 | Education | *(structural)* | structural |  |
| 52 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/forwheelz.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Telemetry to output contract. | `L4.8` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | Driver-risk intelligence | `L4.8` | verbatim |  |
| 4 | 28-feature trip pipeline from vehicle telemetry | `L4.8` | verbatim |  |
| 5 | RF/XGBoost with ablation | `L4.8` | verbatim |  |
| 6 | Output contracts | `L4.8` | verbatim |  |
| 7 | Feature ablations and error analysis | `S5-P3` | verbatim |  |
| 8 | Production-oriented outputs for confidence, risk contributors, and insurer/API integration | `S5-P3` | verbatim |  |
| 9 | Risk-index + DNA-score | `L4.8@4.1` | verbatim |  |
| 10 | Scope | *(structural)* | structural |  |
| 11 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 12 | RF/XGBoost | `L4.8` | verbatim |  |
| 13 | Technology | *(structural)* | structural |  |
| 14 | Previous project | *(structural)* | structural |  |
| 15 | HalalBot | `L4.7` | verbatim |  |
| 16 | Next project | *(structural)* | structural |  |
| 17 | email-MCP | `L4.9` | verbatim |  |
| 18 | The drawing | *(structural)* | structural | Archetype label for the plate (A6 plate). |
| 19 | What it is | *(structural)* | structural | Archetype label for the closing human plane (the T2 close). |
| 20 | Driver-risk intelligence: 28-feature trip pipeline from vehicle telemetry, RF/XGBoost with ablation, output contracts. | `L4.8` | verbatim |  |
| 21 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 22 | Outcome | *(structural)* | structural |  |
| 23 | Driver-risk intelligence with a risk-index + DNA-score, and production-oriented outputs for confidence and risk contributors. | `L4.8@4.1`, `S5-P3` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 24 | Driver-risk intelligence built on a 28-feature trip pipeline from vehicle telemetry, with RF/XGBoost with ablation and explicit output contracts. | `L4.8` | composed | Phrases: 'driver-risk intelligence', '28-feature trip pipeline from vehicle telemetry', 'RF/XGBoost with ablation', 'output contracts' (L4.8). |
| 25 | Random Forest/XGBoost models were evaluated through feature ablations and error analysis, and production-oriented outputs were defined for confidence, risk contributors, and insurer/API integration. | `S5-P3` | verbatim | S5 ForWheelz wording (S5-P3), newest and more specific than the 4.1 wording. |
| 26 | It also exposes a risk-index + DNA-score, developed with feature ablation + error analysis. | `L4.8@4.1` | composed | Phrases: 'risk-index + DNA-score'; 'feature ablation + error analysis' (ledger 4.1, ForWheelz row). |
| 27 | All work | *(structural)* | structural |  |
| 28 | ForWheelz | `L4.8` | verbatim |  |
| 29 | Shipped products & ML systems | *(structural)* | structural |  |
| 30 | Overview | *(structural)* | structural |  |
| 31 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 32 | Problem | *(structural)* | structural |  |
| 33 | Risk has to be read from vehicle telemetry, and the output has to be usable by an insurer's API. | `L4.8` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 34 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 35 | Approach | *(structural)* | structural |  |
| 36 | A 28-feature trip pipeline from vehicle telemetry into RF/XGBoost with ablation, behind explicit output contracts. | `L4.8` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 37 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 38 | The hard part | *(structural)* | structural |  |
| 39 | Models were evaluated through feature ablations and error analysis. | `S5-P3` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 40 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 41 | Evidence | *(structural)* | structural |  |
| 42 | Capabilities & practices | *(structural)* | structural |  |
| 43 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 44 | ForWheelz — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 45 | About | *(structural)* | structural |  |
| 46 | Experience | *(structural)* | structural |  |
| 47 | Work | *(structural)* | structural |  |
| 48 | Skills | *(structural)* | structural |  |
| 49 | Education | *(structural)* | structural |  |
| 50 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/email-mcp.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | Tool-server surface. | `L4.9` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — interface shape only. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | MCP tool server | `L4.9` | verbatim |  |
| 4 | 29 tests | `L4.9` | verbatim |  |
| 5 | Documented | `L4.9` | verbatim |  |
| 6 | Scope | *(structural)* | structural |  |
| 7 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 8 | MCP | `L4.9` | verbatim |  |
| 9 | Technology | *(structural)* | structural |  |
| 10 | Previous project | *(structural)* | structural |  |
| 11 | ForWheelz | `L4.8` | verbatim |  |
| 12 | Next project | *(structural)* | structural |  |
| 13 | Voice agent core | `L4.10` | verbatim |  |
| 14 | Tools are the interface: an MCP tool server. | `L4.9` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 15 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 16 | Problem | *(structural)* | structural |  |
| 17 | A documented MCP tool server with 29 tests. | `L4.9` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 18 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 19 | Approach | *(structural)* | structural |  |
| 20 | 03 / 06 | *(structural)* | structural | Case-study stage serial. |
| 21 | Architecture | *(structural)* | structural |  |
| 22 | NOT YET PUBLISHED | *(structural)* | structural |  |
| 23 | This block is withheld until its source is published on this site. | *(structural)* | structural | Process statement about this site's publication rule; asserts nothing about the person. |
| 24 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 25 | The hard part | *(structural)* | structural |  |
| 26 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 27 | Evidence | *(structural)* | structural |  |
| 28 | An MCP tool server, documented, with 29 tests. | `L4.9` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 29 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 30 | Outcome | *(structural)* | structural |  |
| 31 | All work | *(structural)* | structural |  |
| 32 | email-MCP | `L4.9` | verbatim |  |
| 33 | MCP tool server, 29 tests, documented. | `L4.9` | verbatim |  |
| 34 | Shipped products & ML systems | *(structural)* | structural |  |
| 35 | Overview | *(structural)* | structural |  |
| 36 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 37 | email-MCP — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 38 | About | *(structural)* | structural |  |
| 39 | Experience | *(structural)* | structural |  |
| 40 | Work | *(structural)* | structural |  |
| 41 | Skills | *(structural)* | structural |  |
| 42 | Education | *(structural)* | structural |  |
| 43 | Contact | *(structural)* | structural |  |

### P2 — project detail page `projects/voice-agent-core.html`

| # | Rendered text | Ref | Mode | Note |
|---|---|---|---|---|
| 1 | The audio pipeline, end to end. | `L4.10` | composed | Artefact caption (PROOF_PLAN.md section 4). Names only what the diagram draws; asserts nothing beyond the project's ledger row. |
| 2 | Schematic — structure only. No operational data. | *(structural)* | structural | Mandatory scope caption on every artefact (PROOF_PLAN.md section 5 rule 9). A statement about the drawing, not about the person. |
| 3 | VAD → Whisper → LLM → TTS pipeline | `L4.10` | verbatim |  |
| 4 | Twilio-ready | `L4.10` | verbatim |  |
| 5 | Arabic + English | `L4.10` | verbatim |  |
| 6 | Scope | *(structural)* | structural |  |
| 7 | Describes capability and engineering practice; no client or third-party internals are disclosed. | *(structural)* | structural | Identical on all ten detail pages (PRD 4.4 template); asserts nothing about the person. |
| 8 | VAD → Whisper → LLM → TTS | `L4.10` | verbatim |  |
| 9 | Twilio | `L4.10` | verbatim |  |
| 10 | Technology | *(structural)* | structural |  |
| 11 | Previous project | *(structural)* | structural |  |
| 12 | email-MCP | `L4.9` | verbatim |  |
| 13 | 01 / 06 | *(structural)* | structural | Case-study stage serial. |
| 14 | Problem | *(structural)* | structural |  |
| 15 | Speech has to move through a pipeline before a model can answer. | `L4.10` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 16 | 02 / 06 | *(structural)* | structural | Case-study stage serial. |
| 17 | Approach | *(structural)* | structural |  |
| 18 | VAD → Whisper → LLM → TTS, Twilio-ready, covering Arabic + English. | `L4.10` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 19 | 04 / 06 | *(structural)* | structural | Case-study stage serial. |
| 20 | The hard part | *(structural)* | structural |  |
| 21 | NOT YET PUBLISHED | *(structural)* | structural |  |
| 22 | This block is withheld until its source is published on this site. | *(structural)* | structural | Process statement about this site's publication rule; asserts nothing about the person. |
| 23 | 05 / 06 | *(structural)* | structural | Case-study stage serial. |
| 24 | Evidence | *(structural)* | structural |  |
| 25 | Capabilities & practices | *(structural)* | structural |  |
| 26 | 06 / 06 | *(structural)* | structural | Case-study stage serial. |
| 27 | Outcome | *(structural)* | structural |  |
| 28 | A voice agent pipeline that is Twilio-ready and covers Arabic + English. | `L4.10` | composed | Case-study stage copy. Composed under PRD 3.4 from this project's own ledger / approved-extension phrases; connective verbs only. |
| 29 | Notes | *(structural)* | structural | Archetype label for the margin column (A8 marginalia). |
| 30 | 03 / 06 | *(structural)* | structural | Case-study stage serial. |
| 31 | Architecture | *(structural)* | structural |  |
| 32 | A voice agent pipeline: VAD → Whisper → LLM → TTS. It is Twilio-ready and covers Arabic + English. | `L4.10` | composed | Phrases: 'VAD→Whisper→LLM→TTS pipeline', 'Twilio-ready', 'Arabic + English' (L4.10). |
| 33 | All work | *(structural)* | structural |  |
| 34 | Voice agent core | `L4.10` | verbatim |  |
| 35 | VAD→Whisper→LLM→TTS pipeline, Twilio-ready, Arabic + English. | `L4.10` | verbatim |  |
| 36 | Shipped products & ML systems | *(structural)* | structural |  |
| 37 | Overview | *(structural)* | structural |  |
| 38 | Sources: the owner's own profile, résumé and project notes. | *(structural)* | structural | B2-04 / D5: the human-readable form of the attribution rule. It replaces the visible source-tier token (S1/S2/S3/S5) and the SOURCE TIERS footer legend, which were QA vocabulary published to the visitor. The tier taxonomy still governs the build and still reaches the DOM as data-source-tiers on the attribution rule; it asserts nothing about the person. |
| 39 | Voice agent core — Mohammed Tawfiq Rahmy | `L1.1` | composed | Title = the ledger project name plus the ledger name. |
| 40 | About | *(structural)* | structural |  |
| 41 | Experience | *(structural)* | structural |  |
| 42 | Work | *(structural)* | structural |  |
| 43 | Skills | *(structural)* | structural |  |
| 44 | Education | *(structural)* | structural |  |
| 45 | Contact | *(structural)* | structural |  |

---

## 3. Coverage summary

- mapped factual blocks (with at least one ledger ref): **337**
- structural blocks (assert no fact about the person): **375**
- unsourced rendered lines found by the mechanical checker: **0**
- Tier-B/§9 content: **0 occurrences** (ledger §7 Tier-B names are not present anywhere in the repository)

Notes on the delivered state (owner decisions, `site.config.json`):

- contact = LinkedIn only (`L8.3`); `L8.1`/`L8.2` are **not rendered** and the switch that would render them is asserted in both states by `tests/switch_integrity.py`.
- photo = **included** (`L1.5`, Tier C released by the owner): `docs/assets/profile.jpg`, a self-hosted copy of `sources/linkedin_profile_photo_400.jpg` (sha256 `be1dc0c6…89be`), alt text = `L1.1`.
- Tier-B certifications = **none** (`L7.6` renders nowhere).

