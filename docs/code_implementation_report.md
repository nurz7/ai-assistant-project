# Code Implementation Report

## Date

2026-07-08

## Scope

This report covers the first code update after repositioning the project as:

```text
AI/GIS Copilot for Reservoir Monitoring
```

The work focused on the nearest implementation tasks:

1. Stabilize `/chat` around route + schema + service.
2. Finalize mock/LLM behavior for the new domain.
3. Add a reservoir methodology RAG skeleton with sources.

No SQLite reservoir database, report service, map visualization, or external integrations were added in this step.

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
- reservoir lookup, observation analysis, and report generation return a safe warning because structured reservoir tools are not implemented yet.

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

## Current Limitations

- Reservoir profile lookup is not implemented yet.
- Satellite observation lookup is not implemented yet.
- Area comparison with passport area is not implemented yet.
- Anomaly service is not implemented yet.
- Monitoring report generation is not implemented yet.
- API smoke test passed through a local FastAPI server.
- Streamlit server was started successfully, but browser-level UI submission was not recorded as a full manual E2E test.
- The RAG layer is local lexical retrieval, not embeddings.

## Next Recommended Branch

```text
feature/reservoir-demo-db
```

## Next 3 Implementation Tasks

1. Add SQLite schema and synthetic seed data for `reservoirs`, `satellite_observations`, `area_level_reference`, and optional `alerts`.
2. Implement read-only reservoir service functions: `get_reservoir_summary` and `get_observations`.
3. Implement `compare_area_to_passport` and basic anomaly checks with tests.
