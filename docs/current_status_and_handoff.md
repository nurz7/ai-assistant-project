# Текущее состояние проекта и handoff

Дата обновления: 2026-07-08

## 1. Краткий итог

Проект сейчас называется:

```text
AI/GIS Copilot for Reservoir Monitoring
```

Текущий этап разработки:

```text
Reservoir methodology RAG baseline implemented
```

Это уже не generic support/operations assistant. Проект переориентирован на AI/GIS workflow для мониторинга малых водохранилищ, flood-season analysis, satellite-derived water area, methodology Q&A, citations, refusal behavior и будущие structured reservoir tools.

## 2. Что уже реализовано

В рабочей версии есть:

- FastAPI backend;
- Streamlit UI;
- `POST /chat`;
- thin route + schema + service structure;
- mock/LLM client;
- mock mode по умолчанию;
- reservoir-oriented response schema;
- methodology document loader;
- local lexical retrieval;
- source citations;
- refusal behavior;
- reservoir-specific evaluation dataset;
- backend/unit/integration tests.

Текущий `/chat` умеет отвечать на methodology questions по документам из `data/docs/`.

Пример поддерживаемого вопроса:

```text
What is MNDWI used for in water surface detection?
```

Ожидается:

- `intent = methodology_qa`;
- ответ из retrieved methodology context;
- source citation;
- `mode = mock`.

## 3. Что изменилось в последнем кодовом этапе

Изменены основные файлы:

```text
app/models/schemas.py
app/services/chat_service.py
app/services/llm_client.py
app/services/retrieval_service.py
app/services/document_loader.py
app/core/config.py
app/main.py
ui/streamlit_app.py
data/docs/
evals/questions.yaml
evals/run_evals.py
tests/
docs/code_implementation_report.md
```

Добавлены или закреплены поля ответа:

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

Поддерживаемые intent values:

```text
methodology_qa
reservoir_lookup
observation_analysis
report_generation
unsupported
```

Важно: `reservoir_lookup`, `observation_analysis` и `report_generation` пока возвращают safe refusal/warning, потому что structured reservoir database еще не реализована.

## 4. Methodology documents

Старые support SOP документы заменены на reservoir methodology документы:

```text
data/docs/sentinel2_water_detection.md
data/docs/reservoir_monitoring_workflow.md
data/docs/reservoir_reference_values.md
```

Покрытые темы:

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

## 5. Verification

Автоматические проверки прошли:

```text
python -m pytest -q
24 passed

python -m evals.run_evals
Cases: 24
supported_top1_accuracy: 100.0% (required 90.0%)
unsupported_refusal_accuracy: 100.0% (required 95.0%)
citation_rate: 100.0% (required 100.0%)
PASS
```

API smoke test также был выполнен через локальный FastAPI server:

```text
GET /
POST /chat
```

Проверенный вопрос:

```text
What is MNDWI used for in water surface detection?
```

Результат:

- HTTP 200;
- `mode = mock`;
- `intent = methodology_qa`;
- source document `sentinel2_water_detection.md`;
- source section `MNDWI Water Mask`.

Streamlit server был запущен локально, но browser-level сценарий с ручным вводом вопроса в UI не фиксировался как полноценный E2E test.

## 6. Текущее Git-состояние

В рабочем дереве есть незакоммиченные и неотслеживаемые файлы.

Это ожидаемо для текущей сессии, потому что проект до этого уже содержал незакоммиченный service-layer/RAG набор файлов.

Перед коммитом рекомендуется внимательно разделить изменения по смыслу:

```text
1. Documentation repositioning
2. Reservoir chat schema and methodology RAG baseline
3. Reservoir eval dataset and tests
```

Не использовать `git reset --hard` и не откатывать файлы без явного решения владельца проекта.

## 7. Что еще не реализовано

Не реализовано:

- SQLite reservoir database;
- synthetic reservoir seed data;
- `reservoir_service.py`;
- `get_reservoir_summary`;
- `get_observations`;
- `compare_area_to_passport`;
- `find_area_anomalies`;
- `anomaly_service.py`;
- `report_service.py`;
- real monitoring report generation;
- map/GeoJSON visualization;
- real LLM smoke test.

Текущий проект не должен утверждать, что умеет рассчитывать точный уровень воды. Пока реализована только methodology RAG baseline.

## 8. Следующая ветка

Рекомендуемая следующая ветка:

```text
feature/reservoir-demo-db
```

## 9. Следующие 3 задачи

1. Добавить SQLite schema и synthetic seed data для:

```text
reservoirs
satellite_observations
area_level_reference
alerts
```

2. Реализовать read-only reservoir service:

```text
get_reservoir_summary
get_observations
```

3. Реализовать area comparison и basic anomaly checks:

```text
compare_area_to_passport
find_area_anomalies
```

## 10. Правила для следующей сессии

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

## 11. Команды для проверки

Перед завершением следующего coding этапа запускать:

```bash
python -m pytest -q
python -m evals.run_evals
```

Для локального запуска:

```bash
uvicorn app.main:app --reload
streamlit run ui/streamlit_app.py
```

Если порт `8000` занят, можно использовать другой:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8015
API_URL=http://127.0.0.1:8015/chat streamlit run ui/streamlit_app.py --server.port 8515
```

## 12. Где смотреть детали

Основные документы:

```text
README.md
AGENTS.md
docs/project_scope.md
docs/codex_context.md
docs/architecture.md
docs/roadmap.md
docs/development_log.md
docs/implementation_rules.md
docs/code_implementation_report.md
docs/domain_reservoir_monitoring.md
```

Кодовый отчет последнего этапа:

```text
docs/code_implementation_report.md
```
