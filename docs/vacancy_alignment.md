# Vacancy Alignment

## Purpose

This file explains how the AI/GIS Copilot for Reservoir Monitoring supports job applications and interviews.

The project is designed as a portfolio proof for roles related to:

- AI Engineer;
- AI Specialist;
- AI Solutions Developer;
- AI Implementation Specialist;
- GIS AI / GeoAI roles;
- data analyst or data workflow roles;
- AI evaluation and quality roles.

## Target Role Requirements

Across relevant vacancies, recurring requirements include:

- LLM integration;
- RAG and knowledge-base workflows;
- Python backend development;
- API design;
- Streamlit or lightweight demo UI;
- SQL and structured data workflows;
- document processing;
- domain-specific AI implementation;
- GIS or geospatial data awareness;
- testing and evaluation;
- Git workflow;
- product and business process thinking.

## How This Project Matches

### LLM Integration

Project features:

- mock/LLM client direction;
- provider logic isolated from routes;
- grounded answer generation;
- planned typed settings and provider error handling.

Interview value:

- shows ability to integrate an LLM into an application instead of only using a chat UI.

### RAG

Project features:

- methodology documents;
- document loading;
- chunking;
- retrieval;
- source citations;
- refusal when context is missing.

Interview value:

- shows practical handling of hallucination risk and source-grounded answers.

### FastAPI

Project features:

- backend API;
- `/chat` endpoint;
- planned route/schema/service separation;
- future reservoir and report endpoints.

Interview value:

- shows backend engineering and API design skills.

### Streamlit

Project features:

- demo UI for chat and future reservoir workflows;
- planned source and warning display;
- future report display.

Interview value:

- shows ability to build a quick, understandable product demo.

### SQL and Data Workflow

Project features:

- planned SQLite reservoir demo database;
- reservoir profiles;
- satellite observations;
- area-level reference table;
- alerts table;
- read-only structured tools.

Interview value:

- shows practical data modeling and analytics workflow thinking.

### GIS and Domain Specificity

Project features:

- Sentinel-2 methodology;
- NDWI and MNDWI concepts;
- SCL water class;
- ROI and water mask workflow;
- cloud filtering;
- satellite-derived water area;
- passport area, normal level, dead level, and area-level relationship limitations.

Interview value:

- makes the project more specific and memorable than a generic chatbot.

### Document Processing

Project features:

- methodology/SOP documents;
- source metadata;
- section-aware citations;
- refusal behavior.

Interview value:

- shows how AI can be used with operational knowledge, not only open-ended prompts.

### Evaluation

Project features:

- planned reservoir-specific eval questions;
- citation checks;
- refusal checks;
- calculation checks;
- prompt injection tests;
- latency/basic logging.

Interview value:

- shows production-minded thinking about AI quality and regression risk.

### Git Workflow

Project features:

- feature branch workflow;
- focused PRs;
- documentation updates;
- tests before merge.

Interview value:

- shows readiness for collaborative engineering workflows.

### Product Thinking

Project features:

- clear target users;
- realistic MVP phases;
- synthetic/public-safe data policy;
- no overclaiming;
- human-review limitations.

Interview value:

- shows ability to scope an AI solution around a practical workflow.

## Why This Project Is Stronger Than a Generic Chatbot

A generic chatbot usually shows:

- a prompt box;
- an LLM response;
- limited domain grounding.

This project shows:

- domain-specific AI implementation;
- RAG with citations;
- structured reservoir observations;
- basic calculations and anomaly flagging;
- report generation;
- refusal behavior;
- evaluation and safety planning;
- FastAPI, Streamlit, SQL, and Git workflow.

## Main Portfolio Story

The project can be described as:

> I built an AI/GIS Copilot for Reservoir Monitoring that combines FastAPI, Streamlit, LLM integration, RAG over methodology documents, structured reservoir observations, anomaly checks, and report generation to support satellite-based monitoring workflows.

## CV Bullet Points Draft

- Developed an AI/GIS reservoir monitoring copilot using FastAPI, Streamlit, LLM integration, and planned SQLite workflows for structured observations.
- Designed RAG-based methodology Q&A with source citations and refusal behavior for Sentinel-2, NDWI, MNDWI, SCL water class, ROI, cloud filtering, and water area extraction topics.
- Planned read-only reservoir data tools for profile lookup, satellite observation analysis, passport-area comparison, and anomaly flagging.
- Added evaluation and safety direction covering citation behavior, refusal behavior, calculation checks, prompt injection tests, and basic latency tracking.
- Maintained a portfolio-friendly Git workflow with focused branches, documentation, tests, and synthetic/public-safe demo data.

## Interview Talking Points

### AI Implementation

- How mock mode helps development and public demos.
- How provider-specific LLM logic is isolated.
- Why RAG reduces unsupported answers.

### GIS/Data Workflow

- How satellite-derived water area can support reservoir monitoring.
- Why cloud filtering and ROI quality matter.
- Why passport area is useful but not the same as validated water level.

### Backend Engineering

- Why FastAPI and Pydantic fit the backend.
- Why route handlers should stay thin.
- How services separate retrieval, data lookup, anomaly checks, and report generation.

### Evaluation and Safety

- How to test citations and refusal behavior.
- How to test simple calculation correctness.
- How to avoid overclaiming exact water levels.
- How prompt injection cases can be added to evals.

### Product Thinking

- Why the project targets a specialist workflow instead of a universal agent.
- Why the MVP uses synthetic or public-safe data.
- How the project could be extended later with GeoJSON, map visualization, or Google Earth Engine exports.
