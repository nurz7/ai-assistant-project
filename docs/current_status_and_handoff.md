# Текущее состояние проекта и handoff

Дата обновления: 2026-07-12

## 1. Краткий итог

Проект:

```text
AI/GIS Copilot for Reservoir Monitoring
```

Текущий этап разработки:

```text
Phase 4 monitoring report generation implemented
```

Проект покрывает methodology RAG с citations/refusal behavior, structured-data сценарии и grounded monitoring reports по синтетическим наблюдениям.

## 2. Что реализовано

В рабочей версии есть:

- FastAPI backend;
- Streamlit UI;
- `POST /chat`;
- thin route + schema + service structure;
- mock/LLM client;
- mock mode по умолчанию;
- methodology document loader;
- Unicode-aware local lexical retrieval for English and Russian methodology questions;
- sanitized thesis-informed methodology document and source audit;
- source citations;
- refusal behavior;
- generated local SQLite demo database;
- synthetic seed data for `reservoirs`, `satellite_observations`, `area_level_reference`, and `alerts`;
- read-only reservoir service;
- basic passport-area comparison;
- basic anomaly flagging;
- thesis-informed automatic quality assessment with explicit reasons;
- validation-only sanitized GEE CSV importer and synthetic sample;
- monitoring report service;
- report generation through `/chat` with methodology sources and limitations;
- reservoir-specific tests and evals.

## 3. Что умеет `/chat`

Methodology questions:

```text
What is MNDWI used for in water surface detection?
```

Ожидается:

- `intent = methodology_qa`;
- answer from retrieved methodology context;
- source citation;
- `mode = mock`.

Reservoir profile:

```text
Tasmola reservoir profile
```

Ожидается:

- `intent = reservoir_lookup`;
- synthetic reservoir summary;
- passport area, normal level, dead level, coordinates, notes;
- warnings about synthetic data and water-level limitations.

Observation analysis:

```text
Show Tasmola observations for May 2025.
```

Ожидается:

- `intent = observation_analysis`;
- 3 synthetic Sentinel-2 observations;
- SCL, MNDWI, NDWI water area values;
- cloud percentage;
- method version;
- MNDWI vs passport-area comparison;
- anomaly flags for high cloud and method conflict where relevant.

Report generation:

```text
Generate a monitoring report for Tasmola for May 2025.
```

Возвращает структурированный monitoring report с observations, passport-area comparison, anomaly flags, methodology notes, sources, warnings, limitations, and conclusion.

## 4. Основные файлы Phase 4

```text
app/db/database.py
app/db/seed_data.py
app/services/reservoir_service.py
app/services/report_service.py
app/services/chat_service.py
app/models/schemas.py
data/db/.gitkeep
evals/questions.yaml
evals/run_evals.py
tests/test_reservoir_service.py
tests/test_report_service.py
```

Локальная SQLite база создаётся из seed data при первом обращении по пути:

```text
data/db/reservoir_demo.sqlite
```

Файл базы игнорируется git. Источник demo data находится в `app/db/seed_data.py`.

## 5. Verification

Автоматические проверки:

```text
python -m pytest -q
45 passed

python -m evals.run_evals
Cases: 28
supported_top1_accuracy: 100.0% (required 90.0%)
unsupported_refusal_accuracy: 100.0% (required 95.0%)
citation_rate: 100.0% (required 100.0%)
structured_success_rate: 100.0% (required 100.0%)
calculation_check_rate: 100.0% (required 100.0%)
PASS
```

## 6. Что ещё не реализовано

Не реализовано:

- dedicated `/reports` endpoint;
- map/GeoJSON visualization;
- real LLM smoke test;
- browser-level Streamlit E2E test.
- latency/basic run logging;
- CI automation.

Важно: проект всё ещё не должен утверждать, что рассчитывает точный уровень воды. Satellite-derived water area сравнивается с passport area только как demo decision-support signal.

## 7. Следующая ветка после merge

Текущая ветка:

```text
feature/monitoring-report-generation
```

## 8. Следующие 3 задачи

1. Выполнить manual Streamlit smoke test для report generation.
2. Добавить latency/basic run logging и расширить prompt-injection checks.
3. Добавить CI для pytest и eval runner.

## 9. Правила для следующей сессии

Сохранять ограничения:

- mock mode должен работать без API key;
- все demo data должны быть synthetic или public-safe;
- не подключать реальные government systems;
- не делать destructive SQL;
- не делать exact water level claims без validated area-level relationship;
- route handlers должны оставаться тонкими;
- backend logic должна жить в services;
- новые backend features должны иметь tests;
- docs нужно обновлять вместе с архитектурными изменениями.

## 10. Команды для проверки

Перед завершением coding этапа запускать:

```bash
python -m pytest -q
python -m evals.run_evals
```

Для локального запуска:

```bash
uvicorn app.main:app --reload
streamlit run ui/streamlit_app.py
```

Если порт `8000` занят:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8015
API_URL=http://127.0.0.1:8015/chat streamlit run ui/streamlit_app.py --server.port 8515
```
