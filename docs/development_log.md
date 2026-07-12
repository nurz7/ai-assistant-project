# Development Log

## Purpose

This file tracks development history, project direction, and next steps for the AI/GIS Copilot for Reservoir Monitoring.

It helps the project owner and coding agents understand what has already happened, what changed in project positioning, and what should be built next.

## Project Timeline

### 2026-06-21 - Initial GitHub and FastAPI Setup

Status: completed

Done:

- created local project folder;
- initialized Git repository;
- created GitHub repository;
- added initial FastAPI app;
- added basic `/chat` endpoint;
- created virtual environment;
- added initial dependencies.

Notes:

- project started as a generic AI operations assistant;
- initial focus was proving the backend/API foundation.

### 2026-06-21 - Streamlit UI Added

Status: completed

Done:

- added Streamlit chat interface;
- connected Streamlit UI to FastAPI `/chat`;
- tested frontend-backend flow;
- used feature branch and pull request workflow.

Notes:

- confirmed that a simple user-facing demo can be built quickly;
- response behavior was still placeholder or mock-oriented.

### 2026-06-21 - LLM Client and Service Direction Started

Status: completed or partially implemented in the existing prototype

Done:

- started separating LLM logic from routes;
- introduced `app/services/` direction;
- prepared mock/LLM mode;
- kept local development possible without an API key.

Notes:

- mock mode remains a required feature for the public portfolio repo;
- future provider configuration should use typed settings and `.env.example`.

### 2026-06-21 - First Project Direction Refined

Status: historical

Decision:

The project was initially refined into:

```text
AI Support & Operations Copilot
```

Reason at the time:

- clear internal business workflow;
- good fit for AI implementation roles;
- allowed RAG, API design, SQL/data workflow, and evals.

Current relevance:

- the older support/operations direction has been replaced by the reservoir-monitoring direction;
- some technical work from the old direction may still be useful, especially `/chat`, service separation, mock mode, retrieval, citations, refusal behavior, tests, and eval scaffolding.

### 2026-06-21 to 2026-07-04 - Early RAG and Evaluation Prototype

Status: existing prototype work

Done in the earlier domain:

- separated API route, schemas, and chat service;
- added structured response fields such as sources and warnings;
- added document loading and chunking;
- added local retrieval;
- added grounded answers with citations;
- added refusal behavior when context is missing;
- added automated tests and evaluation scaffolding.

Notes:

- this work may still reference support/SOP documents;
- it should be adapted carefully to reservoir monitoring instead of discarded without review.

### 2026-07-08 - Project Repositioned to Reservoir Monitoring

Status: documentation-only update

New project name:

```text
AI/GIS Copilot for Reservoir Monitoring
```

New direction:

- AI/GIS portfolio project for reservoir monitoring workflows;
- RAG over methodology documents;
- structured reservoir observations;
- area comparison and anomaly flagging;
- monitoring report generation;
- evaluation and safety layer.

Reason:

- stronger connection to the owner's GIS and hydrology background;
- stronger portfolio story for AI Engineer, AI Specialist, GIS AI, and data workflow roles;
- more specific than a generic internal support assistant;
- related to the owner's master's research topic without presenting the repo as an academic-only thesis project.

Documentation updated:

- `README.md`;
- `AGENTS.md`;
- `docs/project_scope.md`;
- `docs/codex_context.md`;
- `docs/architecture.md`;
- `docs/roadmap.md`;
- `docs/development_log.md`;
- `docs/vacancy_alignment.md`;
- `docs/implementation_rules.md`;
- `docs/demo_script.md`;
- `docs/domain_reservoir_monitoring.md`.

No application code was changed in this documentation task.

### 2026-07-08 - Reservoir Chat Schema and Methodology RAG Skeleton

Status: automated checks passed; manual UI smoke test pending

Done:

- updated FastAPI app metadata to `AI/GIS Copilot for Reservoir Monitoring`;
- expanded chat response schema with `intent`, `reservoir`, `calculation_result`, `observations`, `anomaly_flags`, `sources`, and `warnings`;
- kept `/chat` as a thin route calling `chat_service`;
- added simple intent classification for methodology Q&A, reservoir lookup, observation analysis, and report generation;
- kept report requests in safe refusal mode until Phase 4 report generation exists;
- updated mock and real LLM instructions from support/SOP wording to reservoir monitoring methodology wording;
- added `METHODOLOGY_DOCS_PATH` configuration with backward-compatible `SOP_DOCS_PATH` fallback;
- replaced old support SOP demo documents with reservoir methodology documents;
- added topics for Sentinel-2, NDWI, MNDWI, SCL water class, ROI, water mask extraction, cloud filtering, area calculation, passport area, normal level, dead level, area-level relationship, anomaly flagging, and monitoring reports;
- updated tests for the new reservoir domain;
- replaced the old support eval dataset with 24 reservoir-specific retrieval and refusal cases.

Verification:

```text
python -m pytest -q
24 passed

python -m evals.run_evals
24 cases
supported_top1_accuracy: 100.0%
unsupported_refusal_accuracy: 100.0%
citation_rate: 100.0%
PASS
```

### 2026-07-12 - Monitoring Report Generation

Status: automated checks passed; manual UI smoke test pending

Done:

- added `app/services/report_service.py`;
- combined reservoir profile, Sentinel-2 observations, passport-area comparison, anomaly flags, methodology sources, warnings, limitations, and conclusion;
- exposed monitoring report generation through `/chat`;
- preserved deterministic mock-mode behavior without an API key;
- added report service tests and a structured report eval case;
- kept the exact-water-level limitation explicit.

Verification:

```text
python -m pytest -q
36 passed

python -m evals.run_evals
PASS
```

### 2026-07-12 - Thesis Methodology Audit and Multilingual RAG

Status: automated checks passed

Done:

- audited the owner-provided dissertation archive without committing raw research data;
- added a public-safe methodology summary for the Sentinel-2, GEE, QC, and preliminary S-H workflow;
- documented which thesis materials are excluded from the public MVP;
- changed lexical tokenization to support Unicode and Cyrillic;
- added Russian token normalization, safety patterns, retrieval tests, and eval cases;
- ignored the source dissertation archive in Git.

Verification:

```text
python -m pytest -q
38 passed

python -m evals.run_evals
Cases: 28
PASS
```

### 2026-07-12 - Thesis-Informed QC and Safe GEE Import

Status: implemented; automated checks passed

Done:

- added deterministic quality assessment for observation time series;
- exposed QC status and reasons through `/chat`, reports, and Streamlit;
- added transparent demo thresholds for USE, USE_WITH_CAUTION, ROI review, and low-signal exclusion;
- added a validation-only GEE CSV importer with a strict public-safe schema;
- rejected coordinates, real identifiers, levels, and volumes at the import boundary;
- added a synthetic GEE sample and focused service tests.

## Current State

Working or already present in the repository:

- FastAPI backend;
- Streamlit UI;
- basic `/chat` endpoint;
- mock/LLM client;
- service-layer structure for chat, retrieval, document loading, and LLM access;
- reservoir methodology retrieval with citations;
- thesis-informed English/Russian methodology retrieval with citations;
- SQLite-backed reservoir profile and observation lookup;
- passport-area comparison and basic anomaly flags;
- grounded monitoring report generation through `/chat`;
- reservoir-specific tests and eval cases.

Not yet implemented for the reservoir domain:

- latency/basic run logging and CI;
- optional GIS visualization.

## Current Next Steps

Next implementation tasks:

1. Run a manual Streamlit report smoke test.
2. Add latency/basic run logging and extend safety evals.
3. Add CI for pytest and the eval runner.

## Progress Checklist

### Documentation

- [x] reservoir monitoring direction defined
- [x] README updated
- [x] AGENTS instructions updated
- [x] roadmap updated
- [x] architecture updated
- [x] domain overview added
- [ ] screenshots added
- [ ] final demo video recorded

### Backend

- [x] FastAPI app exists
- [x] `/chat` endpoint exists
- [x] service layer audited against reservoir-monitoring schema
- [x] typed settings finalized
- [x] reservoir-specific intent handling added

### UI

- [x] Streamlit app exists
- [x] citations confirmed for reservoir methodology answers
- [x] reservoir observation output added
- [x] report output added
- [ ] optional map visualization added

### RAG

- [x] earlier retrieval prototype exists
- [x] reservoir methodology documents added
- [x] reservoir chunking/retrieval verified
- [x] citations shown in responses
- [x] unsupported reservoir questions refused

### Reservoir Data

- [x] synthetic reservoir data model created
- [x] SQLite database added
- [x] `get_reservoir_summary` added
- [x] `get_observations` added
- [x] `compare_area_to_passport` added
- [x] `find_area_anomalies` added

### Reports

- [x] report service added
- [x] short monitoring report generated
- [x] limitations and sources included

### Evaluation

- [x] earlier eval scaffolding may exist
- [x] reservoir-specific eval questions added
- [x] citation checks added or adapted
- [x] refusal checks added or adapted
- [x] calculation checks added
- [x] prompt injection tests added
- [ ] latency/basic logging added

## Key Decisions

### Decision 1: Keep Existing Repository

Do not restart from zero.

Reason:

- FastAPI and Streamlit foundation already exists;
- mock/LLM direction already exists;
- earlier RAG and eval work can be adapted;
- Git history shows project evolution.

### Decision 2: Reposition to Reservoir Monitoring

Reason:

- more specific and memorable portfolio story;
- aligns with GIS/hydrology background;
- supports AI + data workflow roles;
- demonstrates domain understanding beyond a generic chatbot.

### Decision 3: Keep MVP Practical

Reason:

- a 1-2 month MVP should be realistic;
- methodology RAG, structured demo data, basic anomaly checks, and report generation are enough to show value;
- advanced GIS processing can be optional later.

### Decision 4: Avoid Overclaiming

Reason:

- the assistant is not an official hydrological decision-making system;
- exact water level claims require validated area-level relationship data;
- outputs should include limitations and human-review assumptions.

## Open Questions

- Which LLM provider should be used for the final live demo after mock mode is stable?

## Notes for Future Development

Keep the project narrow.

Every new feature must support the core story:

> AI implementation for reservoir monitoring workflows using RAG, structured observations, anomaly checks, reports, and evaluations.

If a feature does not support that story, do not add it to the MVP.
