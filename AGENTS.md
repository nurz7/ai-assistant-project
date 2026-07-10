# AGENTS.md

## Project Name

AI/GIS Copilot for Reservoir Monitoring

## Project Purpose

This repository is a portfolio project that demonstrates practical AI implementation in a GIS/data workflow connected to reservoir monitoring and flood-season analysis.

The project is related to the owner's master's research topic:

```text
Development of methods for calculating water levels of small reservoirs in Kazakhstan during the flood period.
```

The project must not look like only an academic thesis project. It should be framed as an AI implementation/product prototype for specialists who monitor reservoirs, water infrastructure, satellite observations, and reporting workflows.

## Main Positioning

The assistant helps a GIS analyst, hydrology researcher, water infrastructure specialist, data analyst, or operations/reporting specialist:

1. Ask methodology questions about reservoir monitoring.
2. Get grounded answers from methodology/SOP documents with citations.
3. Understand NDWI, MNDWI, SCL water class, Sentinel-2 processing, ROI, cloud filtering, and water area extraction.
4. Query structured reservoir observations.
5. Compare satellite-derived water area with passport/reference values.
6. Detect basic anomalies or suspicious observations.
7. Generate short monitoring reports for selected reservoirs.
8. Track quality through evaluation questions, refusal behavior, logs, and tests.

## Important Framing

Do not overclaim.

This is:

- a portfolio MVP;
- an AI + GIS + RAG + data workflow implementation;
- a prototype for specialist decision support;
- a demonstration of practical engineering and product thinking.

This is not:

- an official hydrological decision-making system;
- a production scientific model;
- a certified water-level calculation tool;
- a replacement for hydrologists, GIS analysts, or infrastructure specialists.

## Current Stack

- Python
- FastAPI
- Streamlit
- Pydantic
- SQLite planned for synthetic/demo reservoir data
- RAG over methodology documents
- LLM API integration with mock mode
- pytest
- GitHub pull request workflow

## MVP Order

### Phase 0: Documentation and Project Repositioning

Core goal: make the repository clearly about reservoir monitoring.

Required work:

- update README and docs;
- define domain, scope, roadmap, architecture, and coding-agent instructions;
- keep the repository portfolio-oriented and realistic.

### Phase 1: Backend Stabilization

Core goal: keep the backend simple, modular, and reliable.

Required work:

- refactor `/chat` into route + schema + chat service where needed;
- keep Streamlit working;
- keep mock mode working;
- keep route handlers thin;
- keep provider logic inside the LLM client.

### Phase 2: Methodology RAG

Core goal: answer methodology questions from reservoir-monitoring documents.

Required work:

- add synthetic or public-safe methodology/SOP documents;
- implement or adapt loader, chunker, retrieval, citations, and refusal behavior;
- answer only from retrieved context;
- show citations in Streamlit.

### Phase 3: Reservoir Demo Data Tools

Core goal: move from document Q&A to structured reservoir observations.

Required work:

- add SQLite database with synthetic/demo reservoir data;
- add read-only tools:
  - `get_reservoir_summary`;
  - `get_observations`;
  - `compare_area_to_passport`;
  - `find_area_anomalies`;
- do not implement free-form destructive SQL.

### Phase 4: Monitoring Report Generation

Core goal: produce short reservoir monitoring reports from context and observations.

Required work:

- combine RAG context with structured observations;
- include reservoir summary, observations, comparisons, issues, method notes, conclusion, and sources;
- include warnings and limitations.

### Phase 5: Evaluation and Logging

Core goal: show production-minded AI engineering.

Required work:

- add reservoir-specific `evals/questions.yaml`;
- add or adapt a simple eval runner;
- check citations, refusal behavior, calculation correctness, latency, and prompt injection resistance;
- add structured logs where useful.

### Phase 6: Optional GIS Extensions

Core goal: add visual GIS value after the core MVP works.

Optional work:

- simple map visualization;
- GeoJSON support;
- Google Earth Engine export ingestion;
- GeoPandas/Rasterio experiments.

These are not required for the MVP.

## Suggested Data Model

```text
reservoirs
  id
  name
  region
  passport_area_km2
  normal_level_m
  dead_level_m
  latitude
  longitude
  notes

satellite_observations
  id
  reservoir_id
  observation_date
  source
  scl_water_area_km2
  mndwi_area_km2
  ndwi_area_km2
  cloud_percent
  roi_area_km2
  method_version

area_level_reference
  id
  reservoir_id
  area_km2
  level_m
  volume_m3
  source
  reliability_note

alerts
  id
  reservoir_id
  observation_id
  alert_type
  severity
  message
  created_at
```

All demo data must be synthetic or public-safe.

## Required Domain Terms

Use these terms consistently where relevant:

- Sentinel-2
- NDWI
- MNDWI
- SCL water class
- ROI
- water mask
- cloud filtering
- satellite-derived water area
- passport area
- normal level
- dead level
- area-level relationship
- flood period
- reservoir monitoring
- anomaly flagging
- monitoring report

## Coding Rules

1. Keep route handlers thin.
2. Put business logic in services.
3. Keep mock mode working without a paid LLM API key.
4. Use typed Pydantic models for API input/output.
5. Avoid hardcoding secrets.
6. Keep `.env` private and use `.env.example`.
7. Use synthetic or public-safe data only.
8. Do not connect to real government or operational systems in the MVP.
9. Do not perform write actions into external systems.
10. Add tests when adding backend logic.
11. Update relevant docs when changing architecture, scope, or behavior.
12. Prefer small pull-request-sized changes.

## RAG and Safety Rules

- Document-based answers must include citations.
- Minimum source fields should be `document`, `section`, and `chunk_id`.
- If context is missing or weak, the assistant must refuse.
- Do not invent methodology details.
- Do not claim exact water levels without validated area-level relationship data.
- Mention cloud filtering, ROI limitations, method version, and data quality concerns when relevant.
- Human review is required for real operational decisions.

## Non-Goals

Do not build:

- a universal AI agent;
- a production hydrological forecasting system;
- official water level calculations without validated area-level curves;
- integrations with real government systems in MVP;
- workflows using private or confidential data;
- destructive SQL or write actions into external systems;
- automatic final operational decisions;
- a general GIS research notebook collection.

## Target Future Structure

```text
app/
  main.py
  api/
    routes/
      chat.py
      reservoirs.py
      reports.py
  core/
    config.py
  models/
    schemas.py
  services/
    chat_service.py
    llm_client.py
    retrieval_service.py
    reservoir_service.py
    report_service.py
    anomaly_service.py
  db/
    database.py
    seed_data.py

ui/
  streamlit_app.py

data/
  reservoir_demo/
  docs/
  db/
  samples/

evals/
  questions.yaml
  run_evals.py

docs/
```

## How Codex Should Help

When generating code, Codex should:

1. Read this file first.
2. Keep the project aligned with the reservoir-monitoring MVP roadmap.
3. Avoid introducing unrelated frameworks or broad agent features.
4. Preserve mock mode.
5. Keep demo data synthetic or public-safe.
6. Implement RAG with citations and refusal behavior before report generation.
7. Add read-only structured data tools before any advanced GIS features.
8. Add or update tests when adding backend logic.
9. Update documentation when architecture, scope, or behavior changes.
10. Keep the project useful for AI Engineer, AI Specialist, GIS AI, and data workflow roles.
