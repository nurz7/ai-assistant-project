# Product and Technical Decisions

This file records decisions that should remain stable while the reservoir-monitoring MVP is implemented.

## D1: Project Direction

Status: accepted

The project is now:

```text
AI/GIS Copilot for Reservoir Monitoring
```

The project should demonstrate practical AI implementation in a GIS/data workflow connected to reservoir monitoring and flood-season analysis.

It should not be treated as:

- a generic support assistant;
- a universal chatbot;
- a production hydrological forecasting system;
- an official water-level calculation tool.

## D2: Domain Scope

Status: accepted

The MVP focuses on:

- methodology Q&A with citations;
- Sentinel-2, NDWI, MNDWI, SCL water class, ROI, cloud filtering, and water mask concepts;
- structured synthetic reservoir observations;
- satellite-derived water area comparison;
- basic anomaly flagging;
- short monitoring reports;
- evaluation and refusal behavior.

The MVP must not use private, confidential, or unpublished datasets as if they are included in the repository.

## D3: Default Mode and LLM Provider

Status: accepted

The public repository and automated tests use `mock` mode by default.

Reason:

- the project must run without an API key;
- tests should be deterministic;
- recruiters and reviewers should be able to run the demo without paid API access.

Real LLM mode remains isolated in `app/services/llm_client.py`.

When enabled, the real LLM must:

- answer only from retrieved methodology context and structured observations;
- cite chunk IDs for document-grounded answers;
- refuse unsupported questions;
- avoid exact water-level claims without validated area-level reference data.

## D4: Retrieval Before Embeddings

Status: accepted

Use deterministic local lexical retrieval for the first methodology RAG baseline.

Embeddings may be added later only if the evaluation dataset shows that lexical retrieval cannot handle important methodology paraphrases.

Reason:

- local retrieval is simple and inspectable;
- it keeps the portfolio MVP easy to run;
- it avoids unnecessary infrastructure before the workflow is proven.

## D5: Quality Gates

Status: accepted

The committed reservoir methodology evaluation dataset must contain at least 20 cases and pass:

- supported-question top-1 source accuracy: at least 90%;
- unsupported-question refusal accuracy: at least 95%;
- citation presence for supported questions: 100%.

Current baseline:

```text
24 cases
supported_top1_accuracy: 100.0%
unsupported_refusal_accuracy: 100.0%
citation_rate: 100.0%
```

## D6: Chat API Contract

Status: accepted

`POST /chat` returns a structured response:

```text
user_message
answer
mode
intent
sources
reservoir
calculation_result
warnings
```

Accepted intents:

```text
methodology_qa
reservoir_lookup
observation_analysis
report_generation
unsupported
```

The endpoint can orchestrate the demo workflow during the MVP, but route handlers must stay thin and delegate logic to services.

## D7: Structured Reservoir Tools

Status: accepted

Reservoir data tools must be read-only in the MVP.

Planned tools:

```text
get_reservoir_summary
get_observations
compare_area_to_passport
find_area_anomalies
```

Do not implement free-form destructive SQL.

Do not write to real external systems.

## D8: Hydrological Claim Limits

Status: accepted

The assistant may:

- explain methodology;
- show satellite-derived water area estimates;
- compare observed area with passport/reference area;
- flag suspicious observations;
- generate monitoring report drafts with limitations.

The assistant must not:

- claim exact water level without validated area-level relationship data;
- make official safety decisions;
- certify reservoir state;
- present synthetic/demo observations as real operational records.

## D9: Data Safety

Status: accepted

All demo data must be synthetic or public-safe.

Do not commit:

- `.env`;
- API keys;
- private datasets;
- confidential documents;
- sensitive infrastructure records;
- private logs.

## D10: Next Implementation Phase

Status: accepted

The next coding branch should be:

```text
feature/reservoir-demo-db
```

Scope:

1. Add SQLite schema and synthetic seed data.
2. Add read-only reservoir summary and observation lookup.
3. Add area comparison and basic anomaly checks with tests.
