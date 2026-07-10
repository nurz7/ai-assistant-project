# Implementation Rules

## Purpose

This file defines practical implementation rules for the AI/GIS Copilot for Reservoir Monitoring.

Use it to avoid scope creep, unsafe claims, and messy architecture.

## Rule 1: Keep Route Handlers Thin

API route handlers should only:

- receive requests;
- validate input;
- call services;
- return responses.

Do not put retrieval, database, anomaly, report, or LLM-provider logic directly inside route handlers.

## Rule 2: Keep Services Separate

Use separate services for separate responsibilities.

Suggested services:

```text
chat_service.py
llm_client.py
retrieval_service.py
reservoir_service.py
anomaly_service.py
report_service.py
```

## Rule 3: Keep Mock Mode Working

The project must work without a real LLM API key.

Mock mode should be the default for local setup, tests, and portfolio review.

## Rule 4: Do Not Commit Secrets

Never commit:

- `.env`;
- API keys;
- tokens;
- private logs;
- private datasets;
- confidential organization data.

Use `.env.example` for configuration documentation.

## Rule 5: Use Synthetic or Public-Safe Data

All demo data must be synthetic or public-safe.

Do not use:

- private company data;
- confidential government data;
- unpublished research datasets as if they are included in the repo;
- personal data;
- operationally sensitive infrastructure data.

## Rule 6: Prefer Read-Only Workflows

The MVP should not write to external systems.

Allowed:

- read methodology documents;
- read synthetic/demo reservoir database;
- calculate comparisons;
- generate anomaly warnings;
- generate short reports.

Not allowed:

- update real monitoring systems;
- send official alerts;
- write to government or engineering systems;
- delete or modify external records;
- run destructive SQL from user input.

## Rule 7: Add Citations for Methodology Answers

Any answer based on methodology or SOP documents should include sources.

Minimum source fields:

```text
document
section
chunk_id
```

## Rule 8: Refuse Unsupported Questions

If retrieved context is missing or weak, the assistant should say it does not have enough information.

Do not invent:

- methodology details;
- reservoir observations;
- exact water levels;
- official conclusions;
- source references.

## Rule 9: Do Not Overclaim Hydrological Results

The assistant may compare satellite-derived water area with passport/reference area.

The assistant must not claim exact water level unless validated area-level relationship data is available.

When area-level reference data is missing, say that area can be compared but exact level cannot be concluded.

## Rule 10: Surface Data Quality Warnings

Responses should include warnings when relevant:

- cloud percentage is high;
- observation is missing;
- ROI area is incomplete or suspicious;
- NDWI, MNDWI, and SCL water estimates conflict;
- passport area is only a reference value;
- method version is unknown.

## Rule 11: Keep Evaluation Simple but Present

Minimum eval coverage:

- methodology supported question answered with citation;
- unsupported question refused;
- citation-required answer includes source;
- simple area comparison is calculated correctly;
- high cloud percentage produces warning;
- prompt injection request is not followed.

## Rule 12: Update Docs with Architecture Changes

When changing architecture, update relevant docs:

- `README.md`;
- `docs/architecture.md`;
- `docs/codex_context.md`;
- `docs/development_log.md`;
- `docs/roadmap.md` when phase status changes.

## Rule 13: Use Small Pull Requests

Each PR should focus on one change.

Good PR examples:

- `Refactor chat service layer`
- `Add reservoir methodology documents`
- `Add reservoir retrieval sources`
- `Add synthetic reservoir database`
- `Add anomaly service`
- `Add monitoring report service`
- `Add reservoir eval cases`

Bad PR example:

- `Add full GIS platform with RAG, SQL, maps, auth, deployment and forecasting`

## Rule 14: Keep the Project Demo-Friendly

Every MVP feature should support a 2-3 minute demo.

Target demo flow:

1. Ask MNDWI methodology question.
2. Ask unsupported exact water-level question.
3. Show Tasmola observations for May 2025.
4. Compare observed water area with passport area.
5. Generate a short monitoring report for Tasmola.

## Rule 15: Avoid Overengineering

Do not add complex tools before the core workflow works.

Avoid early:

- Kubernetes;
- multi-agent orchestration;
- advanced RBAC;
- production geospatial processing stack;
- complex cloud deployment;
- real external integrations.

## Rule 16: Prioritize Hiring Value

When choosing between tasks, prefer the task that better demonstrates:

- AI implementation;
- RAG;
- API design;
- SQL/data workflow;
- GIS/domain specificity;
- evaluation;
- safety;
- product thinking.

## Rule 17: Keep Public Repository Safe

Before making the repo public, check:

- `.env` is ignored;
- demo data is synthetic or public-safe;
- no private organization names are used as private data sources;
- README is clear;
- setup works from scratch;
- screenshots do not expose private information;
- docs do not imply official hydrological authority.

## Rule 18: Keep Optional GIS Extensions Optional

Map visualization, GeoJSON, Google Earth Engine exports, GeoPandas, and Rasterio are optional after the MVP.

Do not turn the repo into a general GIS research notebook collection.

## Rule 19: Keep Domain Language Precise

Use precise terms:

- satellite-derived water area;
- passport area;
- normal level;
- dead level;
- area-level relationship;
- flood period;
- anomaly flagging;
- monitoring report.

Avoid unsupported terms such as:

- official forecast;
- certified water level;
- final safety decision;
- real-time emergency alerting.

## Rule 20: Run Checks Before Finishing Code Work

For implementation tasks, run relevant checks such as:

```bash
python -m pytest -q
python -m evals.run_evals
```

Use the eval command when evals are present and relevant to the change.
