# Architecture

## High-Level Architecture

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

The architecture is intentionally simple. The goal is to demonstrate a realistic AI/GIS workflow MVP, not to build a complex enterprise platform.

## Main Components

### 1. Streamlit UI

Path:

```text
ui/streamlit_app.py
```

Responsibilities:

- collect user questions;
- call FastAPI endpoints;
- show assistant answers;
- show citations and warnings;
- show reservoir profiles, observations, comparisons, anomaly flags, and later reports;
- stay demo-friendly for a 2-3 minute walkthrough.

The UI should not contain core business logic.

### 2. FastAPI Backend

Path:

```text
app/main.py
```

Responsibilities:

- create the application;
- include routers;
- expose API docs;
- keep startup behavior simple.

### 3. API Routes

Current paths:

```text
app/api/routes/chat.py
app/api/routes/reservoirs.py
app/api/routes/reports.py
```

Responsibilities:

- define endpoints;
- validate request and response models;
- call services;
- return structured responses.

Routes should not contain retrieval logic, database logic, report logic, or LLM-provider logic.

### 4. Chat Service / Workflow Service

Target path:

```text
app/services/chat_service.py
```

Responsibilities:

- coordinate `/chat` behavior;
- classify the user intent at a simple rule-based or LLM-assisted level;
- call retrieval for methodology Q&A;
- call reservoir data service for profile and observation questions;
- call anomaly service for area comparison checks;
- call report service for report generation;
- attach sources, warnings, and structured fields.

Initial intents:

```text
methodology_qa
reservoir_lookup
observation_analysis
report_generation
unsupported
```

### 5. LLM Client

Target path:

```text
app/services/llm_client.py
```

Responsibilities:

- keep mock mode working;
- support a real LLM provider when configured;
- isolate provider-specific API calls;
- normalize configuration and provider errors;
- keep prompts grounded in retrieved methodology context and structured observations.

Mock mode must remain the default for local setup and portfolio demos without paid API access.

### 6. Retrieval Service

Target path:

```text
app/services/retrieval_service.py
```

Responsibilities:

- load methodology documents;
- split documents into chunks;
- search relevant chunks;
- return source metadata;
- support refusal behavior when relevant context is weak or missing.

Required source metadata:

```text
document
section
chunk_id
```

### 7. Reservoir Data Service

Target paths:

```text
app/services/reservoir_service.py
app/db/database.py
app/db/seed_data.py
```

Responsibilities:

- read synthetic/demo reservoir profiles;
- read satellite observations;
- expose read-only data access methods;
- keep SQL queries parameterized;
- compare satellite-derived water area with passport area;
- flag high cloud percentage and conflicting NDWI, MNDWI, and SCL estimates;
- return warnings for missing or incomplete data.

Suggested tables:

```text
reservoirs
satellite_observations
area_level_reference
alerts
```

### 8. Anomaly Logic

Current MVP location:

```text
app/services/reservoir_service.py
```

Responsibilities:

- compare satellite-derived water area with passport/reference area;
- flag observations much lower or higher than expected;
- flag high cloud percentage;
- flag conflicting NDWI, MNDWI, and SCL area estimates;
- flag missing observations;
- avoid claiming exact water level unless validated area-level relationship data is available.

This can be split into `app/services/anomaly_service.py` later if the anomaly logic grows beyond the basic MVP checks.

### 9. Report Service

Target path:

```text
app/services/report_service.py
```

Responsibilities:

- generate short monitoring reports;
- combine reservoir profile, observations, anomaly checks, and methodology notes;
- include limitations and sources;
- produce concise outputs suitable for an analyst workflow.

### 10. Evaluation Layer

Target path:

```text
evals/
```

Responsibilities:

- store evaluation questions;
- run local regression checks;
- check citation presence;
- check refusal behavior;
- check simple calculation correctness;
- check prompt injection resistance;
- track latency or basic run metadata.

## Data Flow: Methodology Q&A

```text
User asks methodology question
  ->
Streamlit sends POST /chat
  ->
Chat service detects methodology_qa
  ->
Retrieval service searches methodology chunks
  ->
LLM client answers using retrieved context, or mock mode formats grounded answer
  ->
Chat service attaches sources and warnings
  ->
FastAPI returns structured response
  ->
Streamlit displays answer and citations
```

If retrieval returns no reliable context, the assistant refuses and does not invent an answer.

## Data Flow: Reservoir Observation Analysis

```text
User asks about reservoir and date/period
  ->
Chat service detects observation_analysis
  ->
Reservoir data service reads profile and observations
  ->
Anomaly service checks cloud percentage, area differences, and method conflicts
  ->
LLM client or report formatter explains the result
  ->
Response includes structured reservoir, calculation result, warnings, and sources when available
```

## Data Flow: Monitoring Report

```text
User requests monitoring report
  ->
Chat service detects report_generation
  ->
Reservoir service loads profile and observations
  ->
Retrieval service loads method notes
  ->
Anomaly service produces flags
  ->
Report service generates concise report
  ->
Response includes report text, warnings, and sources
```

## Suggested Future API Endpoints

```text
GET /
POST /chat
GET /reservoirs
GET /reservoirs/{reservoir_id}
GET /reservoirs/{reservoir_id}/observations
POST /reservoirs/{reservoir_id}/compare-area
GET /reservoirs/{reservoir_id}/alerts
POST /reports/monitoring
POST /evals/run
```

For the MVP, `/chat` can orchestrate most demo workflows before separate reservoir/report endpoints are added.

## Main Architectural Decisions

### Decision 1: Keep FastAPI and Streamlit

FastAPI provides a clean API layer and Pydantic validation. Streamlit provides a fast demo interface for recruiters and interviewers.

### Decision 2: Keep Mock Mode

Mock mode allows the project to run without paid API access, supports tests, and makes the public repo easier to evaluate.

### Decision 3: Start with Local Retrieval

Local lexical retrieval is acceptable for the first reservoir methodology RAG slice. Embeddings can be added later if evaluation shows a clear need.

### Decision 4: Use Read-Only Structured Tools

Reservoir profile and observation tools should be read-only. The MVP should not run free-form destructive SQL or write into external systems.

### Decision 5: Keep Hydrological Claims Limited

The assistant can compare water area estimates and flag anomalies. It must not claim exact water levels or official operational decisions without validated data and human review.
