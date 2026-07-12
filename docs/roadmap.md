# Roadmap

## Main Goal

Build a portfolio MVP that shows practical AI implementation for a GIS/data workflow connected to reservoir monitoring and flood-season analysis.

The project should be understandable to recruiters, hiring managers, and technical interviewers as:

- an LLM application;
- a RAG system with citations and refusal behavior;
- a FastAPI and Streamlit implementation;
- a SQL/data workflow prototype;
- a domain-specific AI assistant for reservoir monitoring;
- a production-minded project with tests, evaluations, and documentation.

## Current Phase

Phase 0 documentation and repositioning is complete. Phase 1 service-layer stabilization, Phase 2 methodology RAG, Phase 3 synthetic reservoir demo data tools, and Phase 4 monitoring report generation are implemented for the reservoir-monitoring direction.

The next implementation work should complete Phase 5 logging, safety evaluation, and CI, after a manual Streamlit report smoke test.

## Phase 0: Documentation and Project Repositioning

Status: completed

Tasks:

- [x] rename project positioning to `AI/GIS Copilot for Reservoir Monitoring`;
- [x] update README;
- [x] update AGENTS instructions;
- [x] update project scope;
- [x] update architecture document;
- [x] update Codex context;
- [x] update roadmap;
- [x] update development log;
- [x] update vacancy alignment;
- [x] update implementation rules;
- [x] update demo script;
- [x] add domain reservoir monitoring document.

Definition of done:

- project direction is clear;
- docs explain practical value, not only research value;
- Codex can understand what to build next;
- docs do not overclaim current implementation;
- all demo data requirements are synthetic or public-safe.

## Phase 1: Service-Layer Refactor

Status: implemented; manual UI smoke test pending

Recommended branch:

```text
feature/service-layer-refactor
```

Tasks:

- [x] audit current `/chat` implementation;
- [x] keep route handlers thin;
- [x] ensure request and response schemas live in `app/models/schemas.py`;
- [x] ensure chat orchestration lives in `app/services/chat_service.py`;
- [x] finalize mock/LLM client with typed settings;
- [x] keep `/chat` working;
- [x] keep Streamlit working;
- [x] preserve mock mode as default;
- [x] update tests for the public chat contract.

Definition of done:

- `/chat` works in mock mode;
- Streamlit can call backend successfully;
- backend code is modular;
- settings are typed and do not expose secrets;
- tests pass.

## Phase 2: Methodology RAG

Status: skeleton implemented; manual UI smoke test pending

Tasks:

- [x] add synthetic/public-safe reservoir methodology documents;
- [x] include topics such as Sentinel-2, NDWI, MNDWI, SCL water class, ROI, water mask extraction, cloud filtering, satellite-derived water area, passport area, normal level, dead level, and area-level relationship limitations;
- [x] adapt or implement document loader;
- [x] adapt or implement chunker;
- [x] implement retrieval over methodology chunks;
- [x] return source citations;
- [x] enforce refusal behavior when context is missing;
- [x] show citations in Streamlit response rendering;
- [x] add tests for supported and unsupported methodology questions.

Definition of done:

- user can ask methodology questions;
- supported answers include sources;
- unsupported questions are refused;
- answers do not invent methodology details;
- local tests pass.

## Phase 3: Reservoir Demo Database and Read-Only Tools

Status: implemented

Tasks:

- [x] create SQLite schema for synthetic/demo reservoir data;
- [x] add `reservoirs` table;
- [x] add `satellite_observations` table;
- [x] add `area_level_reference` table;
- [x] add `alerts` table if needed;
- [x] seed demo data for a small number of reservoirs such as Tasmola;
- [x] implement `get_reservoir_summary`;
- [x] implement `get_observations`;
- [x] implement `compare_area_to_passport`;
- [x] implement `find_area_anomalies`;
- [x] add tests for data access and calculations.

Definition of done:

- reservoir profile lookup works from synthetic data;
- observation lookup works by reservoir and period;
- area comparison returns clear values and units;
- high cloud, missing observations, and conflicting methods can be flagged;
- no destructive SQL or external writes exist.

## Phase 4: Monitoring Report Generation

Status: implemented; manual UI smoke test pending

Tasks:

- [x] implement report service;
- [x] generate short reports for reservoir and period;
- [x] include reservoir summary;
- [x] include available observations;
- [x] include SCL, MNDWI, and NDWI water area estimates;
- [x] compare with passport/reference values;
- [x] include anomaly flags;
- [x] include methodological notes and sources;
- [x] include limitations and short conclusion;
- [x] expose report through `/chat`.

Definition of done:

- user can ask for a short monitoring report;
- report is concise and structured;
- report includes warnings and limitations;
- report does not claim exact water level unless validated area-level data exists.

## Phase 5: Evals, Logging, and Safety

Status: partially implemented

Tasks:

- [x] create reservoir-specific `evals/questions.yaml`;
- [x] add methodology supported questions;
- [x] add unsupported questions;
- [x] add citation-required checks;
- [x] add calculation checks;
- [x] add initial prompt injection attempts;
- [x] add thesis-informed Russian methodology retrieval and multilingual eval cases;
- [x] add thesis-informed deterministic QC and structured quality status checks;
- [x] adapt or create `evals/run_evals.py`;
- [x] track citation behavior;
- [x] track refusal behavior;
- [x] track calculation correctness;
- [ ] track latency and basic run metadata;
- [ ] add CI when the local suite is stable.

Definition of done:

- eval runner can be executed locally;
- results show citation and refusal behavior;
- calculation checks catch simple regressions;
- prompt injection cases are included;
- project looks production-minded without overengineering.

## Phase 6: Optional GIS Visualization

Status: optional future work

Tasks:

- [ ] add simple map visualization in Streamlit;
- [ ] support GeoJSON reservoir or ROI display;
- [x] add a validation-only sanitized Google Earth Engine CSV import contract;
- [ ] persist explicitly approved synthetic/public-safe GEE imports;
- [ ] optionally use GeoPandas or Rasterio for local geospatial files;
- [ ] add screenshots for portfolio presentation.

Definition of done:

- GIS visualization supports the reservoir-monitoring story;
- map does not distract from the core AI/RAG/data workflow;
- any public geospatial source is documented clearly.

## Final Portfolio Package

Status: planned

Tasks:

- [ ] add final screenshots;
- [ ] record short demo video;
- [ ] polish README;
- [ ] add final architecture diagram;
- [ ] prepare interview talking points;
- [ ] prepare CV bullet points.

Definition of done:

- project can be shown in 2-3 minutes;
- project can be explained in an interview;
- GitHub repo is clear, safe, and professionally scoped.
