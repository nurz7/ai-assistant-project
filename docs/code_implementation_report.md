# Code Implementation Report

## Date

2026-07-10

## Scope

This report covers the first code update after repositioning the project as:

```text
AI/GIS Copilot for Reservoir Monitoring
```

The work focused on the nearest implementation tasks:

1. Stabilize `/chat` around route + schema + service.
2. Finalize mock/LLM behavior for the new domain.
3. Add a reservoir methodology RAG skeleton with sources.

The initial RAG step did not include the reservoir database. The Phase 3 update now adds synthetic SQLite-backed reservoir data tools. Report service, map visualization, and external integrations are still out of scope for this step.

## What Changed

### 1. Chat Response Schema

Updated:

- `app/models/schemas.py`

Added structured fields:

```text
intent
reservoir
calculation_result
warnings
sources
```

Why:

The assistant should not return only plain text. Reservoir monitoring workflows need structured metadata for methodology answers, future reservoir lookup, future calculations, and warnings.

### 2. Chat Service

Updated:

- `app/services/chat_service.py`

Added simple intent classification:

```text
methodology_qa
reservoir_lookup
observation_analysis
report_generation
unsupported
```

Current behavior:

- methodology questions use retrieval;
- unsupported methodology questions are refused;
- reservoir lookup and observation analysis use synthetic SQLite demo data;
- report generation returns a safe Phase 4 warning.

Why:

This keeps `/chat` useful now while preparing the API contract for the next phase.

### 3. Mock/LLM Client

Updated:

- `app/services/llm_client.py`

Changes:

- replaced support/SOP wording with reservoir monitoring methodology wording;
- kept mock mode working;
- kept real LLM mode grounded in retrieved context;
- added instruction not to claim exact water levels without validated area-level reference data.

Why:

The public demo must work without an API key, but the real LLM path should already follow the correct domain rules.

### 4. Configuration

Updated:

- `app/core/config.py`
- `.env.example`

Added:

```text
METHODOLOGY_DOCS_PATH=data/docs
```

Kept backward-compatible fallback to `SOP_DOCS_PATH`.

Why:

The project no longer uses generic SOP documents as the main domain. The new name makes the purpose clearer while avoiding breakage in older local setups.

### 5. Methodology Documents

Updated:

- `data/docs/`

Replaced old support SOP demo documents with reservoir monitoring methodology documents:

```text
sentinel2_water_detection.md
reservoir_monitoring_workflow.md
reservoir_reference_values.md
```

Covered topics:

- Sentinel-2;
- NDWI;
- MNDWI;
- SCL water class;
- ROI;
- water mask extraction;
- cloud filtering;
- satellite-derived water area;
- passport area;
- normal level;
- dead level;
- area-level relationship;
- anomaly flagging;
- monitoring report.

Why:

The RAG layer should answer questions from the new project domain, not from the old support/operations prototype.

### 6. Retrieval Behavior

Updated:

- `app/services/retrieval_service.py`

Changes:

- adapted token aliases to reservoir monitoring terms;
- renamed retrieval purpose from SOP retrieval to methodology retrieval;
- added a lightweight safety filter for secrets, confidential data, destructive requests, exact water-level lookups, and not-yet-implemented structured data requests.

Why:

The retriever should support methodology Q&A, but it should not answer questions that require structured observation data or unsafe actions.

### 7. UI Text

Updated:

- `ui/streamlit_app.py`

Changes:

- updated title and page text to reservoir monitoring;
- added display for `intent`;
- kept source and warning display.

Why:

The demo UI should match the new project direction and show the structured response contract.

### 8. Tests and Evals

Updated:

- `tests/test_chat_api.py`
- `tests/test_chat_service.py`
- `tests/test_chat_integration.py`
- `tests/test_document_loader.py`
- `tests/test_llm_client.py`
- `tests/test_retrieval_service.py`
- `evals/questions.yaml`
- `evals/run_evals.py`

Changes:

- replaced support-domain test examples with reservoir methodology examples;
- added checks for `intent`;
- verified safe refusal for not-yet-implemented report requests;
- replaced the old support eval dataset with 24 reservoir-specific cases.

Why:

The code should now be tested against the actual project story, not the previous support-copilot story.

## Verification

Commands run:

```bash
python -m pytest -q
python -m evals.run_evals
```

Results:

```text
24 passed

Cases: 24
supported_top1_accuracy: 100.0% (required 90.0%)
unsupported_refusal_accuracy: 100.0% (required 95.0%)
citation_rate: 100.0% (required 100.0%)
PASS
```

These results describe the initial methodology RAG baseline before Phase 3.

## Current Limitations

- Monitoring report generation is not implemented yet.
- Dedicated report and reservoir endpoints are not implemented yet; structured tools are exposed through `/chat`.
- Basic anomaly checks live in `reservoir_service.py`; they can be split into a dedicated anomaly service later if needed.
- API smoke test passed through a local FastAPI server.
- Streamlit server was started successfully, but browser-level UI submission was not recorded as a full manual E2E test.
- The RAG layer is local lexical retrieval, not embeddings.

## Phase 3 Update: Reservoir Demo Database

Detailed Phase 3 report:

```text
docs/phase3_reservoir_demo_db_report.md
```

Added:

- `app/db/database.py`;
- `app/db/seed_data.py`;
- `app/services/reservoir_service.py`;
- generated local SQLite path `data/db/reservoir_demo.sqlite`;
- synthetic seed records for `reservoirs`, `satellite_observations`, `area_level_reference`, and `alerts`;
- read-only service functions:
  - `get_reservoir_summary`;
  - `get_observations`;
  - `compare_area_to_passport`;
  - `find_area_anomalies`;
- structured response fields:
  - `observations`;
  - `anomaly_flags`;
- Streamlit rendering for observation tables and anomaly flags;
- structured eval checks for observation lookup and calculation correctness.

The SQLite file is generated from seed data and ignored by git. This keeps the synthetic data transparent in source code while still giving the app a real local SQL workflow.

## Phase 3 Verification

Commands run:

```bash
python -m pytest -q
python -m evals.run_evals
```

Results:

```text
33 passed

Cases: 24
supported_top1_accuracy: 100.0% (required 90.0%)
unsupported_refusal_accuracy: 100.0% (required 95.0%)
citation_rate: 100.0% (required 100.0%)
structured_success_rate: 100.0% (required 100.0%)
calculation_check_rate: 100.0% (required 100.0%)
PASS
```

## Next Recommended Branch

```text
feature/monitoring-report-generation
```

## Next 3 Implementation Tasks

1. Implement `report_service.py`.
2. Generate short monitoring reports from RAG context, reservoir profile, observations, comparisons, anomaly flags, warnings, and limitations.
3. Add tests/evals for report generation and exact-water-level refusal behavior.
