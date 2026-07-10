# Project Scope

## Project Name

AI/GIS Copilot for Reservoir Monitoring

## Short Description

An AI/GIS portfolio project for reservoir monitoring workflows. The assistant combines LLM integration, RAG over methodology documents, structured reservoir observations, anomaly checks, and report generation to support satellite-based monitoring of small reservoirs.

## Main Problem

Reservoir monitoring during the flood period requires specialists to combine several types of information:

- methodology and SOP documents;
- Sentinel-2 observations;
- NDWI, MNDWI, and SCL water class outputs;
- ROI and cloud filtering decisions;
- satellite-derived water area calculations;
- passport area and reference reservoir information;
- short reporting workflows for analysts and managers.

This work is often fragmented across documents, spreadsheets, notebooks, GIS tools, and manual reports. The project shows how an AI assistant can support the workflow while keeping the human specialist responsible for interpretation and final decisions.

## Proposed Solution

Build a focused assistant that combines:

- methodology Q&A with citations;
- refusal when the knowledge base does not support an answer;
- structured reservoir profile lookup;
- satellite observation lookup;
- comparison between observed water area and passport/reference area;
- anomaly flagging for suspicious observations;
- short monitoring report generation;
- evaluation and logging for quality control.

## Target Users

Primary users:

- GIS analyst;
- hydrology researcher;
- water infrastructure specialist;
- data analyst;
- operations/reporting specialist;
- government or engineering organization analyst.

## Core Workflows

### Workflow 1: Methodology Q&A with Citations

User asks about Sentinel-2, SCL water class, NDWI, MNDWI, ROI, water mask extraction, cloud filtering, area calculation, or limitations.

Acceptance criteria:

- assistant retrieves relevant methodology/SOP chunks;
- answer is based only on retrieved context;
- response includes source citations;
- assistant refuses if information is missing.

### Workflow 2: Reservoir Profile

User asks about a reservoir.

Acceptance criteria:

- assistant returns structured information such as name, region, passport area, coordinates when available, available observation dates, and notes;
- assistant uses only synthetic or public-safe demo data;
- response includes warnings for missing fields.

### Workflow 3: Satellite Observation Analysis

User asks about one reservoir and date or period.

Acceptance criteria:

- assistant returns SCL water area, MNDWI area, NDWI area, cloud percentage, ROI area, and method version when data exists;
- assistant explains limitations;
- assistant does not invent missing observations.

### Workflow 4: Area Comparison and Anomaly Flagging

Assistant compares observed water area with passport/reference area.

Acceptance criteria:

- assistant flags observed area much lower than passport area;
- assistant flags observed area much higher than expected;
- assistant flags high cloud percentage;
- assistant flags conflicting NDWI/MNDWI/SCL results;
- assistant flags missing observations;
- assistant does not claim exact water level unless validated area-level reference data is available.

### Workflow 5: Monitoring Report Generation

User asks for a short monitoring report, for example:

```text
Generate a monitoring report for Tasmola for May 2025.
```

Acceptance criteria:

- report includes reservoir summary;
- report lists available observations;
- report summarizes water area estimates;
- report compares observations with reference/passport values;
- report lists detected issues;
- report includes methodological notes and sources;
- report ends with a short conclusion and limitations.

### Workflow 6: Evaluation and Safety

Acceptance criteria:

- evaluation dataset includes methodology questions;
- unsupported questions are refused;
- citation-required answers include sources;
- calculation checks verify simple comparisons;
- prompt injection attempts are tested;
- logs or eval reports help track regressions.

## MVP Scope

### Phase 0: Documentation and Project Repositioning

Included:

- README and documentation update;
- reservoir-monitoring scope;
- architecture direction;
- roadmap;
- Codex instructions;
- domain overview.

Not included:

- code refactor;
- database creation;
- API behavior changes.

### Phase 1: Backend Stabilization

Included:

- route/schema/service separation;
- stable `/chat` endpoint;
- mock mode;
- typed settings;
- tests for request and response contracts.

Not included:

- reservoir database;
- report service;
- GIS visualization.

### Phase 2: Methodology RAG

Included:

- synthetic/public-safe methodology documents;
- ingestion, chunking, retrieval, citations;
- refusal behavior;
- Streamlit source display.

Not included:

- private datasets;
- production search infrastructure;
- broad GIS notebook collection.

### Phase 3: Reservoir Demo Data Tools

Included:

- SQLite schema for synthetic/demo reservoirs;
- read-only lookup and calculation tools;
- basic anomaly checks.

Not included:

- free-form destructive SQL;
- real government system integration;
- write actions to external systems.

### Phase 4: Monitoring Report Generation

Included:

- short reports for selected reservoirs and periods;
- structured observations;
- RAG-based method notes;
- warnings and limitations.

Not included:

- official hydrological conclusions;
- automated operational decisions.

### Phase 5: Evaluation and Logging

Included:

- reservoir-specific eval questions;
- citation and refusal checks;
- calculation checks;
- latency tracking;
- prompt injection tests.

Not included:

- enterprise observability stack;
- full scientific validation pipeline.

### Phase 6: Optional GIS Extensions

Included only after MVP:

- map visualization;
- GeoJSON support;
- Google Earth Engine export ingestion;
- optional GeoPandas/Rasterio experiments.

## Non-Goals

The project should not become:

- a universal AI agent;
- a production hydrological forecasting system;
- an official water level calculation tool without validated area-level curves;
- a system connected to real government operations in the MVP;
- a repository containing private or confidential datasets;
- a tool that performs write actions into external systems;
- a system that makes final operational decisions automatically;
- a general GIS research notebook collection.

## Success Criteria

The project is successful when it can show:

1. A clear AI + GIS/data workflow problem.
2. A working FastAPI and Streamlit assistant.
3. Methodology RAG with citations.
4. Honest refusal on unsupported questions.
5. Structured reservoir demo data lookup.
6. Basic area comparison and anomaly flagging.
7. Short monitoring report generation.
8. Evaluation questions for citations, refusal, calculations, and prompt injection.
9. Clear documentation for recruiters, hiring managers, and technical interviewers.

## Data Safety Criteria

- Use synthetic or public-safe demo data only.
- Do not reference private company data.
- Do not claim confidential or unpublished datasets are included in the repo.
- Document any future public data source clearly before using it.
- Keep `.env` private.

## Portfolio Story

The project should be explainable in one sentence:

> I built an AI/GIS Copilot for Reservoir Monitoring that answers methodology questions with citations, queries structured reservoir observations, compares satellite-derived water area with passport values, flags suspicious observations, and generates short monitoring reports with clear limitations.
