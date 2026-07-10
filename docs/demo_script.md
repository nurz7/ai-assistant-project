# Demo Script

## Purpose

This file describes a 2-3 minute demo for the AI/GIS Copilot for Reservoir Monitoring.

The demo should be understandable for recruiters, hiring managers, GIS/data specialists, and technical interviewers.

## Demo Goal

Show that the project is not just a chatbot.

It is a focused AI implementation for a reservoir monitoring workflow. It combines methodology RAG, citations, structured observations, simple area comparisons, anomaly warnings, and report generation.

## Setup

Run backend:

```bash
uvicorn app.main:app --reload
```

Run Streamlit:

```bash
streamlit run ui/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

## 30-Second Pitch

> I built an AI/GIS Copilot for Reservoir Monitoring. It supports reservoir-monitoring workflows by answering methodology questions with citations, querying structured satellite observations, comparing water area estimates with passport values, flagging suspicious observations, and generating short monitoring reports. It is a portfolio MVP, not an official hydrological decision system.

## Demo Structure

### Step 1: Methodology Question

Ask:

```text
What is MNDWI used for in water surface detection?
```

Expected assistant behavior:

- retrieves methodology context;
- explains MNDWI at a high level;
- mentions water surface detection and built-up/background noise reduction if supported by the source;
- includes citations;
- avoids unsupported claims.

Say:

> This shows RAG over methodology documents. The assistant should answer from retrieved context and provide sources.

### Step 2: Unsupported Exact Water-Level Question

Ask:

```text
What was the exact water level of unknown reservoir X on 2020-01-01?
```

Expected assistant behavior:

- refuses or says it does not have enough information;
- does not invent a reservoir;
- does not claim exact water level;
- may explain that exact water level requires validated observations or area-level relationship data.

Say:

> This refusal behavior is important because the project must not overclaim hydrological results.

### Step 3: Reservoir Observation Question

Ask:

```text
Show Tasmola observations for May 2025.
```

Expected assistant behavior:

- returns available observations from synthetic/demo data when implemented;
- includes SCL water area, MNDWI area, NDWI area, cloud percentage, ROI area, and method version;
- warns if observations are missing or incomplete.

Say:

> This moves the assistant from document Q&A into a structured GIS/data workflow.

### Step 4: Comparison Question

Ask:

```text
Compare observed water area with passport area.
```

Expected assistant behavior:

- identifies the relevant reservoir and observation context if available;
- compares satellite-derived water area with passport/reference area;
- returns value difference and percentage difference when data exists;
- flags high cloud percentage, large difference, or conflicting NDWI/MNDWI/SCL values;
- avoids claiming exact water level unless validated area-level data exists.

Say:

> The assistant supports analysis, but it does not make final operational decisions.

### Step 5: Monitoring Report

Ask:

```text
Generate a short monitoring report for Tasmola.
```

Expected assistant behavior:

- includes reservoir summary;
- lists available observations;
- summarizes water area estimates;
- compares observed area with passport/reference area;
- lists detected issues;
- includes methodological notes;
- includes a short conclusion;
- includes sources and limitations.

Say:

> This report generation step shows how RAG and structured observations can support a reporting workflow.

## Current Demo Status

Currently present in the repository:

- FastAPI backend;
- Streamlit UI;
- `/chat` endpoint;
- mock/LLM client;
- reservoir-oriented response schema with `intent`, `sources`, `reservoir`, `calculation_result`, and `warnings`;
- reservoir-specific methodology documents;
- local methodology retrieval;
- source citations;
- refusal behavior;
- reservoir-specific tests and evals.

Planned for the reservoir-monitoring demo:

- synthetic Tasmola demo observations;
- passport-area comparison;
- anomaly flagging;
- monitoring report generation.

## Final Demo Checklist

Before recording or showing the final demo:

- [ ] backend runs without errors;
- [ ] Streamlit UI runs without errors;
- [ ] mock mode works without API key;
- [x] methodology question returns source citation;
- [x] unsupported exact water-level question is refused;
- [ ] Tasmola observations are returned from synthetic/demo data;
- [ ] comparison with passport area is calculated correctly;
- [ ] high cloud or conflicting method results produce warnings;
- [ ] monitoring report includes sources and limitations;
- [x] local tests pass;
- [x] local evals pass;
- [ ] README setup instructions are current;
- [ ] demo data is synthetic or public-safe;
- [ ] `.env` is not committed.

## Short Technical Explanation

Use this explanation during an interview:

> The backend is FastAPI with a thin route layer and services for chat orchestration, retrieval, LLM provider access, reservoir data, anomaly checks, and report generation. Streamlit is used for the demo UI. The assistant uses RAG for methodology answers, structured SQLite data for reservoir observations, and simple rule-based checks for anomalies. Mock mode keeps the demo reproducible without paid API access.
