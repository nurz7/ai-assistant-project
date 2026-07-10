# Phase 3 Report: Reservoir Demo Database and Read-Only Tools

Дата: 2026-07-10

Ветка:

```text
feature/reservoir-demo-db
```

Коммит:

```text
7e0fbe1 feat: add reservoir demo data tools
```

## 1. Краткий итог

На этом этапе проект перешёл от простого methodology RAG к первому полноценному AI + data workflow.

До Phase 3 ассистент умел отвечать на методологические вопросы по документам: Sentinel-2, NDWI, MNDWI, SCL water class, ROI, cloud filtering, passport area и ограничения area-level relationship.

После Phase 3 ассистент дополнительно умеет работать с синтетическими структурированными данными:

- показывать профиль водохранилища;
- возвращать спутниковые наблюдения;
- сравнивать satellite-derived water area с passport area;
- находить базовые anomaly flags;
- отдавать эти данные через `/chat` и Streamlit UI.

Важно: данные синтетические. Это portfolio MVP, а не официальный гидрологический инструмент.

## 2. Зачем был нужен этот этап

Методологический RAG показывает, что ассистент умеет отвечать из документов с citations. Но для AI/GIS portfolio project этого недостаточно.

Реальный рабочий процесс специалиста по reservoir monitoring обычно состоит не только из чтения методики. Ему также нужно смотреть таблицы наблюдений, сравнивать значения, замечать подозрительные сцены и готовить короткие выводы.

Поэтому Phase 3 добавляет структурированный слой данных. Это показывает, что проект умеет:

- работать с SQL/database workflow;
- отделять RAG-ответы от deterministic calculations;
- не выдумывать наблюдения через LLM;
- возвращать typed API responses;
- сохранять безопасные ограничения: read-only tools, no destructive SQL, synthetic data only.

## 3. Что было сделано

### 3.1. Добавлен SQLite database layer

Добавлены файлы:

```text
app/db/__init__.py
app/db/database.py
app/db/seed_data.py
data/db/.gitkeep
```

В `app/db/database.py` добавлена схема SQLite для таблиц:

```text
reservoirs
satellite_observations
area_level_reference
alerts
```

В `app/db/seed_data.py` добавлены synthetic demo records для нескольких водохранилищ:

- Tasmola;
- Koksu Demo Reservoir;
- Sarybulak Demo Reservoir.

Как это работает:

1. Приложение берёт путь к базе из `RESERVOIR_DB_PATH`.
2. Если SQLite-файла ещё нет, он создаётся локально.
3. Таблицы создаются через `CREATE TABLE IF NOT EXISTS`.
4. Seed data добавляется только если таблица `reservoirs` пустая.

Почему так:

- SQLite достаточно для portfolio MVP и не требует внешнего сервера;
- seed data хранится в коде, поэтому демо воспроизводимо;
- generated `.sqlite` файл игнорируется git, чтобы не хранить бинарную базу;
- вся demo data синтетическая и public-safe.

### 3.2. Добавлен путь к demo database в config

Обновлены:

```text
app/core/config.py
.env.example
.gitignore
```

Добавлена настройка:

```text
RESERVOIR_DB_PATH=data/db/reservoir_demo.sqlite
```

В `.gitignore` добавлено:

```text
data/db/*.sqlite
data/db/*.sqlite-*
```

Почему так:

- путь к базе не должен быть захардкожен внутри service layer;
- локальную базу можно заменить через `.env`;
- generated database не должна попадать в репозиторий;
- source of truth для demo data остаётся в `seed_data.py`.

### 3.3. Расширены Pydantic response schemas

Обновлён файл:

```text
app/models/schemas.py
```

Расширены модели:

- `ReservoirReference`;
- `CalculationResult`;
- `ChatResponse`.

Добавлены новые модели:

```text
ReservoirObservation
AnomalyFlag
```

Теперь `/chat` может вернуть не только текстовый `answer`, но и структурированные поля:

```text
reservoir
calculation_result
observations
anomaly_flags
warnings
```

Почему так:

- UI и тесты должны получать данные в предсказуемом формате;
- наблюдения и anomaly flags лучше передавать как structured objects, а не как текст;
- это готовит основу для Phase 4 report generation;
- typed responses снижают риск сломать API-контракт.

### 3.4. Добавлен read-only reservoir service

Добавлен файл:

```text
app/services/reservoir_service.py
```

Реализованы функции:

```text
get_reservoir_summary
get_observations
compare_area_to_passport
find_area_anomalies
```

Также добавлены helper-функции:

```text
list_reservoir_names
extract_reservoir_name
```

Как это работает:

- `get_reservoir_summary` ищет водохранилище по имени и возвращает профиль;
- `get_observations` возвращает Sentinel-2 observations по reservoir and period;
- `compare_area_to_passport` берёт последнее наблюдение в периоде и считает percent difference между MNDWI area и passport area;
- `find_area_anomalies` проверяет cloud percentage, deviation from passport area и conflict между SCL, MNDWI, NDWI.

Почему так:

- route handler должен оставаться thin;
- SQL-запросы должны быть parameterized;
- LLM не должен считать или выдумывать табличные значения;
- deterministic calculations проще тестировать;
- read-only tools безопаснее для MVP, чем free-form SQL.

### 3.5. Добавлена базовая anomaly flagging логика

В `reservoir_service.py` добавлены правила:

```text
HIGH_CLOUD_THRESHOLD = 40.0
MODERATE_CLOUD_THRESHOLD = 30.0
PASSPORT_AREA_WARNING_PERCENT = 15.0
PASSPORT_AREA_HIGH_PERCENT = 30.0
METHOD_CONFLICT_PERCENT = 20.0
```

Проверяются три типа проблем:

- `high_cloud`;
- `passport_area_deviation`;
- `method_conflict`.

Пример:

если cloud cover высокий, observation получает warning, потому что water mask может быть ненадёжной.

Почему так:

- это простые и понятные проверки для MVP;
- они хорошо связаны с domain story: cloud filtering, water mask quality, SCL/NDWI/MNDWI conflict;
- они не требуют production science model;
- они не делают точных water-level claims.

### 3.6. `/chat` подключён к structured data tools

Обновлён файл:

```text
app/services/chat_service.py
```

Теперь intent routing работает так:

- `methodology_qa` -> retrieval over `data/docs/`;
- `reservoir_lookup` -> `get_reservoir_summary`;
- `observation_analysis` -> observations + comparison + anomaly flags;
- `report_generation` -> safe Phase 4 warning;
- `unsupported` -> refusal.

Примеры поддерживаемых запросов:

```text
Tasmola reservoir profile
Show Tasmola observations for May 2025.
Compare Tasmola MNDWI area to passport area for May 2025.
```

Почему так:

- один `/chat` endpoint остаётся главным demo interface;
- бизнес-логика всё равно живёт в services;
- RAG и SQL tools не смешиваются;
- report generation пока не включён, чтобы не overclaim.

### 3.7. Streamlit UI показывает structured outputs

Обновлён файл:

```text
ui/streamlit_app.py
```

UI теперь отображает:

- assistant answer;
- intent;
- reservoir object;
- calculation result;
- observations table;
- anomaly flags table;
- citations;
- warnings.

Почему так:

- portfolio demo должен показывать не только текст, но и данные;
- observations и anomaly flags удобнее смотреть таблицей;
- warnings видны пользователю сразу;
- UI остаётся простым и не содержит business logic.

### 3.8. Обновлены evals

Обновлены:

```text
evals/questions.yaml
evals/run_evals.py
```

Раньше eval runner проверял только methodology retrieval:

- top-1 source accuracy;
- refusal accuracy;
- citation rate.

Теперь добавлены structured checks:

- `structured_success_rate`;
- `calculation_check_rate`.

Добавлены structured cases:

```text
tasmola-may-observations
tasmola-may-passport-comparison
tasmola-profile
```

Почему так:

- новые SQL/data features тоже должны иметь regression checks;
- calculation correctness нельзя проверять только глазами;
- evals теперь показывают не только RAG quality, но и deterministic workflow quality.

### 3.9. Добавлены tests

Добавлен файл:

```text
tests/test_reservoir_service.py
```

Обновлены:

```text
tests/test_chat_service.py
tests/test_chat_integration.py
```

Проверяется:

- reservoir summary lookup;
- observations filtering by period;
- MNDWI vs passport-area calculation;
- high cloud and method conflict flags;
- reservoir name extraction;
- unknown reservoir behavior;
- `/chat` structured observation flow.

Почему так:

- backend logic должна иметь tests;
- synthetic database должна быть воспроизводимой;
- `/chat` contract должен оставаться стабильным;
- regressions в calculations должны ловиться автоматически.

### 3.10. Обновлена документация

Обновлены:

```text
README.md
docs/architecture.md
docs/code_implementation_report.md
docs/codex_context.md
docs/current_status_and_handoff.md
docs/decisions.md
docs/development_log.md
docs/roadmap.md
docs/vacancy_alignment.md
```

Почему так:

- проектная документация должна совпадать с фактическим состоянием кода;
- roadmap теперь показывает Phase 3 как implemented;
- next step теперь Phase 4 monitoring report generation;
- handoff должен помогать следующей coding session, а не отправлять её делать уже завершённую работу.

## 4. Что изменилось в пользовательском поведении

До Phase 3:

```text
Show Tasmola observations for May 2025.
```

возвращал safe refusal, потому что structured reservoir tools ещё не были реализованы.

После Phase 3 этот запрос возвращает:

- `intent = observation_analysis`;
- reservoir profile;
- 3 Sentinel-2 observations for May 2025;
- SCL/MNDWI/NDWI area values;
- cloud percentage;
- method version;
- latest MNDWI vs passport-area comparison;
- anomaly flags;
- warnings about synthetic data and water-level limitations.

При этом запрос:

```text
Generate a monitoring report for Tasmola for May 2025.
```

всё ещё возвращает Phase 4 warning, потому что полноценный report service ещё не реализован.

## 5. Почему не был добавлен free-form SQL

Free-form SQL специально не добавлялся.

Причины:

- MVP должен быть безопасным;
- пользователь не должен выполнять destructive SQL;
- portfolio project должен показывать controlled tools, а не универсальный database agent;
- read-only functions проще тестировать и объяснять;
- это соответствует AGENTS.md: do not implement destructive SQL or write actions into external systems.

## 6. Почему не считается точный уровень воды

Проект сравнивает satellite-derived water area с passport area, но не делает exact water level calculation.

Причина:

точный уровень воды требует validated area-level relationship data. В текущем MVP есть только synthetic demo reference table, поэтому любые output values должны восприниматься как demonstration and decision-support signals.

В ответах сохраняется warning:

```text
Do not treat satellite-derived water area as an exact water level without a validated area-level relationship and human review.
```

## 7. Проверка результата

Команды:

```bash
python -m pytest -q
python -m evals.run_evals
```

Результат:

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

## 8. Как проверить вручную

Запустить backend:

```bash
uvicorn app.main:app --reload
```

Запустить UI:

```bash
streamlit run ui/streamlit_app.py
```

Примеры вопросов:

```text
What is MNDWI used for in water surface detection?
Tasmola reservoir profile
Show Tasmola observations for May 2025.
Compare Tasmola MNDWI area to passport area for May 2025.
Generate a monitoring report for Tasmola for May 2025.
```

Ожидаемое поведение:

- methodology question возвращает citations;
- profile question возвращает structured reservoir data;
- observations question возвращает таблицу observations;
- comparison question возвращает calculation result;
- report question пока возвращает Phase 4 warning.

## 9. Ограничения

Текущие ограничения:

- данные синтетические;
- SQLite создаётся локально из seed data;
- dedicated `/reservoirs` endpoint пока не добавлен;
- dedicated `/reports` endpoint пока не добавлен;
- report generation пока не реализован;
- anomaly checks базовые и rule-based;
- нет production hydrological model;
- нет exact water level calculation;
- нет map/GeoJSON visualization;
- browser-level Streamlit E2E test не автоматизирован.

## 10. Следующий этап

Следующая рекомендуемая ветка:

```text
feature/monitoring-report-generation
```

Следующие задачи:

1. Добавить `app/services/report_service.py`.
2. Генерировать short monitoring report для reservoir and period.
3. Комбинировать:
   - reservoir summary;
   - observations;
   - MNDWI/SCL/NDWI values;
   - passport-area comparison;
   - anomaly flags;
   - methodology notes;
   - citations;
   - warnings and limitations.
4. Добавить tests/evals для report generation.
5. Сохранять refusal для exact water level claims без validated area-level relationship.

