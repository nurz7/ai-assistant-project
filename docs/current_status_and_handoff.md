# Текущее состояние проекта и handoff

Дата обновления: 2026-07-10

## 1. Краткий итог

Проект:

```text
AI/GIS Copilot for Reservoir Monitoring
```

Текущий этап разработки:

```text
Phase 3 reservoir demo database and read-only tools implemented
```

Проект уже покрывает methodology RAG с citations/refusal behavior и первые structured-data сценарии по синтетическим наблюдениям водохранилищ.

## 2. Что реализовано

В рабочей версии есть:

- FastAPI backend;
- Streamlit UI;
- `POST /chat`;
- thin route + schema + service structure;
- mock/LLM client;
- mock mode по умолчанию;
- methodology document loader;
- local lexical retrieval;
- source citations;
- refusal behavior;
- generated local SQLite demo database;
- synthetic seed data for `reservoirs`, `satellite_observations`, `area_level_reference`, and `alerts`;
- read-only reservoir service;
- basic passport-area comparison;
- basic anomaly flagging;
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

Пока возвращает safe refusal/warning. Это Phase 4.

## 4. Основные файлы Phase 3

```text
app/db/database.py
app/db/seed_data.py
app/services/reservoir_service.py
app/services/chat_service.py
app/models/schemas.py
data/db/.gitkeep
evals/questions.yaml
evals/run_evals.py
tests/test_reservoir_service.py
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
33 passed

python -m evals.run_evals
Cases: 24
supported_top1_accuracy: 100.0% (required 90.0%)
unsupported_refusal_accuracy: 100.0% (required 95.0%)
citation_rate: 100.0% (required 100.0%)
structured_success_rate: 100.0% (required 100.0%)
calculation_check_rate: 100.0% (required 100.0%)
PASS
```

## 6. Что ещё не реализовано

Не реализовано:

- full monitoring report service;
- combining RAG methodology notes with structured observations in generated reports;
- dedicated `/reports` endpoint;
- map/GeoJSON visualization;
- real LLM smoke test;
- browser-level Streamlit E2E test.

Важно: проект всё ещё не должен утверждать, что рассчитывает точный уровень воды. Satellite-derived water area сравнивается с passport area только как demo decision-support signal.

## 7. Следующая ветка после merge

Рекомендуемая следующая ветка:

```text
feature/monitoring-report-generation
```

## 8. Следующие 3 задачи

1. Реализовать `report_service.py`.
2. Сгенерировать короткий monitoring report из reservoir summary, observations, comparison, anomaly flags, methodology notes, sources, warnings, and limitations.
3. Добавить tests/evals для report generation и отказа от exact water level claims.

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
