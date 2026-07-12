# Codex Context

## Purpose of This File

This file gives coding agents practical context for working on this repository without drifting away from the reservoir-monitoring MVP.

## Current Project Direction

The project is now positioned as:

```text
AI/GIS Copilot for Reservoir Monitoring
```

It is a portfolio project that demonstrates practical AI implementation in a GIS/data workflow connected to reservoir monitoring and flood-season analysis.

The assistant should support methodology Q&A, structured reservoir observation lookup, area comparison, anomaly flagging, and short monitoring reports. It must not be treated as a generic chatbot or production hydrological decision system.

## Current Implementation State

The existing repository already contains an early FastAPI and Streamlit assistant prototype.

Known current state:

- FastAPI backend exists;
- Streamlit UI exists;
- `/chat` endpoint exists;
- mock/LLM client exists and defaults to mock mode;
- service-oriented structure exists for chat, retrieval, document loading, and LLM access;
- reservoir-oriented response schema includes intent, sources, reservoir, calculation result, observations, anomaly flags, and warnings;
- reservoir methodology documents exist in `data/docs/`;
- local retrieval, citations, refusal behavior, tests, and eval cases are implemented for the methodology RAG skeleton;
- SQLite-backed synthetic reservoir data tools are implemented for profiles, observations, passport-area comparison, and anomaly flagging.

Important: do not connect this MVP to real government, operational, private, or destructive systems.

## Next Best Task

Next recommended coding branch:

```text
feature/monitoring-report-generation
```

Next three implementation tasks:

1. Implement `report_service.py`.
2. Generate short monitoring reports from methodology context, reservoir profile, observations, comparisons, anomaly flags, warnings, and limitations.
3. Add tests/evals for report generation and refusal of exact water-level claims.

The previous recommended tasks, service-layer stabilization, mock/LLM settings, methodology RAG, and reservoir demo data tools, are implemented for the current MVP baseline.

## Target Folder Structure

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
  project_scope.md
  codex_context.md
  architecture.md
  roadmap.md
  development_log.md
  vacancy_alignment.md
  implementation_rules.md
  demo_script.md
  domain_reservoir_monitoring.md
```

## Service Layer Refactor Plan

Keep route handlers thin.

Target responsibilities:

- `app/api/routes/chat.py`: receive request, validate with Pydantic, call service, return response.
- `app/models/schemas.py`: define request, response, source, reservoir, calculation, and warning schemas.
- `app/services/chat_service.py`: decide workflow intent and coordinate retrieval, data services, LLM client, and reports.
- `app/services/llm_client.py`: isolate mock and real provider behavior.
- `app/core/config.py`: load typed settings and defaults.

Required behavior:

- `/chat` continues to work;
- Streamlit continues to work;
- mock mode works without API key;
- unsupported questions get safe refusals;
- code remains easy to explain in an interview.

## Methodology RAG Plan

Purpose:

Answer methodology questions about reservoir monitoring using grounded context.

Initial document topics:

- Sentinel-2 basics for water monitoring;
- NDWI and MNDWI high-level explanation;
- SCL water class and its limitations;
- ROI definition and water mask extraction;
- cloud filtering;
- satellite-derived water area calculation;
- passport area, normal level, dead level, and area-level relationship limitations;
- flood period monitoring workflow.

Required retrieval behavior:

- load synthetic or public-safe Markdown documents;
- split into chunks with document, section, and chunk ID metadata;
- retrieve relevant chunks;
- answer only from retrieved context;
- include sources;
- refuse if retrieved context is missing or weak.

## Reservoir Data Tool Plan

Use SQLite with synthetic/demo data.

Suggested tables:

```text
reservoirs
satellite_observations
area_level_reference
alerts
```

Initial read-only tools:

- `get_reservoir_summary(name: str)`
- `get_observations(name: str, start_date: str | None, end_date: str | None)`
- `compare_area_to_passport(name: str, observation_id: int | None)`
- `find_area_anomalies(name: str | None)`

Rules:

- no free-form destructive SQL;
- no writes to external systems;
- all data must be synthetic or public-safe;
- return clear warnings when data is missing or incomplete.

## Evaluation Plan

Reservoir-specific evals should check:

- methodology answers include citations;
- unsupported questions are refused;
- prompt injection attempts are not followed;
- simple calculations are correct;
- reservoir lookup uses structured data, not invented facts;
- high cloud percentage triggers warnings;
- assistant does not claim exact water level without area-level reference data.

Suggested evaluation categories:

```text
methodology_supported
methodology_unsupported
citation_required
reservoir_lookup
observation_analysis
calculation_check
refusal_behavior
prompt_injection
```

## Suggested Future Chat Response Schema

```json
{
  "user_message": "string",
  "answer": "string",
  "mode": "mock_or_llm",
  "intent": "methodology_qa | reservoir_lookup | observation_analysis | report_generation | unsupported",
  "sources": [
    {
      "document": "string",
      "section": "string",
      "chunk_id": "string"
    }
  ],
  "reservoir": {
    "name": "string",
    "region": "string"
  },
  "calculation_result": {
    "metric": "string",
    "value": 0.0,
    "unit": "string",
    "explanation": "string"
  },
  "warnings": []
}
```

For early phases, only `user_message`, `answer`, `mode`, `intent`, `sources`, and `warnings` may be required.

## Domain Rules for Responses

The assistant may say:

- satellite-derived water area estimate;
- area appears lower or higher than passport/reference area;
- observation may be unreliable because cloud percentage is high;
- exact water level cannot be concluded without validated area-level relationship data.

The assistant must not say:

- exact water level is known when it is not in validated data;
- a reservoir is officially safe or unsafe;
- a government or engineering organization has made a decision;
- private or unpublished data was used when it is not included.

## Development Workflow

Use focused feature branches:

```text
feature/service-layer-refactor
feature/methodology-rag
feature/reservoir-demo-db
feature/monitoring-report-generation
feature/evaluation-and-logging
feature/gis-visualization
```

Before opening a PR:

- run tests relevant to the change;
- verify mock mode;
- update docs if scope or architecture changed;
- confirm no `.env`, private data, or generated database artifacts are accidentally committed unless intentionally added as safe demo files.
