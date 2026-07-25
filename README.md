# AI/GIS Copilot for Reservoir Monitoring

An AI/GIS portfolio project for reservoir monitoring workflows. The assistant combines LLM integration, RAG over methodology documents, structured reservoir observations, anomaly checks, and report generation to support satellite-based monitoring of small reservoirs.

## Why This Project Exists

Reservoir monitoring during the flood period often requires analysts to combine methodology documents, satellite observations, reservoir reference data, and short reporting workflows. This project shows how a focused AI assistant can support that work without pretending to replace hydrological experts or official decision-making systems.

The project is related to the owner's master's research topic:

```text
Development of methods for calculating water levels of small reservoirs in Kazakhstan during the flood period.
```

The repository is framed as an AI implementation and product prototype, not only as an academic thesis artifact. It demonstrates how LLMs, retrieval, structured data, API design, and evaluation can be applied to a GIS/data workflow connected to reservoir monitoring.

## Target Users

- GIS analyst
- Hydrology researcher
- Water infrastructure specialist
- Data analyst
- Operations or reporting specialist
- Government or engineering organization analyst

## Core Use Cases

### 1. Methodology Q&A with Citations

Users can ask questions about Sentinel-2, NDWI, MNDWI, SCL water class, ROI selection, water mask extraction, cloud filtering, water area calculation, and method limitations.

The assistant should:

- retrieve relevant methodology or SOP chunks;
- answer only from retrieved context;
- provide citations;
- refuse when the knowledge base does not contain enough information.

### 2. Reservoir Profile

Users can ask about a reservoir and receive structured reference information:

- name;
- region;
- passport area;
- coordinates when available;
- available observation dates;
- notes and limitations.

### 3. Satellite Observation Analysis

Users can ask about a reservoir and date or period. The assistant should return satellite-derived water area values when demo data exists:

- SCL water area;
- MNDWI area;
- NDWI area;
- cloud percentage;
- ROI area;
- method version;
- limitations.

### 4. Area Comparison and Anomaly Flagging

The assistant should compare observed satellite-derived water area with passport or reference area and flag suspicious observations, such as:

- observed area much lower than passport area;
- observed area much higher than expected;
- high cloud percentage;
- conflicting NDWI, MNDWI, and SCL results;
- missing observations.

The assistant must not claim exact water level unless validated area-level relationship data is available.

### 5. Monitoring Report Generation

Users can request a short monitoring report for a selected reservoir and period. The report should include:

- reservoir summary;
- available observations;
- water area estimates;
- comparison with reference or passport values;
- detected issues;
- methodological notes;
- short conclusion;
- sources.

### 6. Evaluation and Safety

The project should include evaluation questions for:

- methodology questions;
- unsupported questions;
- citation-required answers;
- calculation checks;
- refusal behavior;
- prompt injection attempts.

## Current Status

Implemented in the existing repository:

- FastAPI backend;
- basic `/chat` endpoint;
- Streamlit UI;
- mock/LLM-ready client;
- service-oriented backend structure;
- reservoir-oriented chat response schema with `intent`, `sources`, `reservoir`, `calculation_result`, `observations`, `anomaly_flags`, and `warnings`;
- reservoir methodology documents for Sentinel-2, NDWI, MNDWI, SCL water class, ROI, cloud filtering, area calculation, reference values, and reporting;
- local methodology retrieval with source citations;
- thesis-informed multilingual methodology retrieval for English and Russian questions;
- documented source audit that excludes real coordinates, observations, and preliminary levels from the public demo;
- SQLite schema and synthetic seed data for demo reservoir observations;
- read-only reservoir tools for profiles, observations, passport-area comparison, and anomaly flagging;
- thesis-informed automatic QC with transparent demo status categories;
- sanitized, validation-only GEE CSV import contract with a synthetic sample;
- grounded monitoring report generation from methodology and structured data;
- refusal behavior for unsupported and unsafe requests;
- structured `/chat` run metadata and latency logs without request or response content;
- reservoir-specific test and evaluation dataset with 28 methodology cases plus structured-data and report checks.

Repository repositioning completed in this branch:

- project repositioned from a generic support/operations copilot to `AI/GIS Copilot for Reservoir Monitoring`;
- MVP scope, architecture, roadmap, demo script, and coding-agent instructions aligned to reservoir monitoring;
- backend, methodology RAG, structured demo data tools, tests, and evals updated for the reservoir-monitoring direction.

Not yet implemented for the reservoir domain:

- GIS visualization.

GitHub Actions validates the repository on pushes and pull requests by running the test suite and reservoir evaluation checks.

## Planned Roadmap

### Phase 0: Documentation and Project Repositioning

- Update README and docs.
- Define domain, scope, roadmap, architecture, and Codex instructions.

### Phase 1: Backend Stabilization

- Refactor FastAPI backend into route, schema, and service layers where needed.
- Keep `/chat` working.
- Keep Streamlit working.
- Keep mock mode working.

### Phase 2: Methodology RAG

- Add synthetic or public-safe methodology documents.
- Implement loader, chunker, retrieval, citations, and refusal behavior for reservoir monitoring.
- Show citations in Streamlit.

### Phase 3: Reservoir Demo Data Tools

- Add SQLite database with synthetic/demo reservoir data.
- Add read-only tools:
  - `get_reservoir_summary`;
  - `get_observations`;
  - `compare_area_to_passport`;
  - `find_area_anomalies`.
- Do not implement destructive SQL or free-form database write actions.

### Phase 4: Monitoring Report Generation

- Generate short reservoir monitoring reports from RAG context and structured observations.
- Include warnings, limitations, and sources.

### Phase 5: Evaluation and Logging

- Add reservoir-specific `evals/questions.yaml`.
- Add or adapt a simple eval runner.
- Track citation behavior, refusal behavior, calculation correctness, latency, and prompt injection resistance.

### Phase 6: Optional GIS Extensions

- Add simple map visualization or GeoJSON support.
- Optionally support Google Earth Engine exports.
- Optionally explore GeoPandas or Rasterio after the MVP is stable.

## Tech Stack

- Python
- FastAPI
- Streamlit
- Pydantic
- SQLite for synthetic reservoir demo data
- Local lexical RAG first, embeddings optional later
- LLM API integration with mock mode
- pytest
- GitHub pull request workflow

## Architecture Overview

```text
User
  ->
Streamlit UI
  ->
FastAPI backend
  ->
Chat service / workflow service
  ->
LLM client
  ->
Retrieval service
  ->
Reservoir data service
  ->
Report service
  ->
Evaluation layer
```

Expected future structure:

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

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install development dependencies when working on tests:

```bash
pip install -r requirements-dev.txt
```

Create a local environment file:

```bash
cp .env.example .env
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

Run the Streamlit UI:

```bash
streamlit run ui/streamlit_app.py
```

Open the UI:

```text
http://localhost:8501
```

## Safety and Limitations

- This is not an official hydrological decision-making system.
- This is not a production scientific model.
- The assistant must not claim exact water levels unless validated area-level curves are available.
- Demo data must be synthetic or public-safe.
- The MVP must not connect to real government systems.
- The MVP must not use private, confidential, or unpublished datasets as if they are included in the repo.
- The assistant should refuse unsupported questions and show limitations for cloudy or incomplete observations.
- Human expert review is required for real reservoir monitoring decisions.

## Portfolio Value

This project demonstrates:

- practical LLM integration;
- RAG with citations and refusal behavior;
- AI applied to a GIS/data workflow;
- FastAPI backend design;
- Streamlit demo UI;
- SQL/data modeling for structured observations;
- simple anomaly checks;
- report generation;
- evaluation and safety thinking;
- product framing for a realistic 1-2 month MVP.
