# QA Portfolio — Skeleton

**Ситников Сергей Алексеевич**
Telegram: @ssrjkk | Email: ray013lefe@gmail.com

---

Монорепо с заготовками для 7 пайплайнов. Каждый пайплайн - отдельная директория,
независимый CI workflow, своя инфраструктура.

## Пайплайны

| Пайплайн       | Стек                            | Статус     | CI                          |
|----------------|---------------------------------|------------|-----------------------------|
| api            | pytest + requests + jsonschema  | скелет     | .github/workflows/api.yml   |
| db             | pytest + psycopg2               | скелет     | .github/workflows/db.yml    |
| kafka          | pytest + kafka-python           | скелет     | .github/workflows/kafka.yml |
| load           | locust                          | скелет     | .github/workflows/load.yml  |
| k8s            | pytest + kubernetes             | скелет     | .github/workflows/k8s_smoke.yml |
| crossbrowser   | selenium + Grid                 | скелет     | .github/workflows/crossbrowser.yml |
| logs           | pytest + kibana REST API        | скелет     | .github/workflows/logs.yml  |

## Структура

```
pipelines/
  api/            -> CRUD, контракты, авторизация
  db/             -> консистентность UI/API/DB, целостность данных
  kafka/          -> события, async flow, DLQ
  load/           -> locust tasks, threshold проверка
  k8s/            -> smoke после деплоя, healthcheck
  crossbrowser/   -> Selenium Grid, chrome/firefox/edge
  logs/           -> анализ Kibana после прогона
```

## Запуск конкретного пайплайна

```bash
# API
pytest pipelines/api/ -m api -v

# DB (нужен PostgreSQL)
docker-compose up -d postgres
pytest pipelines/db/ -m db -v

# Kafka (нужен Kafka)
docker-compose up -d kafka zookeeper
pytest pipelines/kafka/ -m kafka -v

# Load
locust -f pipelines/load/locustfile.py --headless --users 50 --run-time 60s --host http://localhost:8080

# Cross-browser (нужен Selenium Grid)
docker-compose up -d selenium-hub chrome firefox edge
pytest pipelines/crossbrowser/ -m crossbrowser -v

# K8s smoke
pytest pipelines/k8s/ -m k8s -v

# Log analysis
pytest pipelines/logs/ -m logs -v
```

## Что нужно сделать для каждого пайплайна

### api
- [ ] Заполнить `http_client.py` - методы GET/POST/PUT/DELETE
- [ ] Добавить авторизацию в conftest.py (получить токен)
- [ ] Заполнить JSON схемы в `schema_validator.py`
- [ ] Реализовать тесты (убрать NotImplementedError)
- [ ] Подключить schemathesis для OpenAPI

### db
- [ ] Реализовать `db_client.py` (psycopg2 + pool)
- [ ] Добавить фикстуру `db` в conftest.py
- [ ] Написать реальные SQL запросы в тестах

### kafka
- [ ] Реализовать `kafka_client.py` (Producer + Consumer)
- [ ] Добавить фикстуры producer/consumer в conftest.py
- [ ] Определить реальные топики и схемы событий

### load
- [ ] Заполнить endpoint'ы в `locustfile.py`
- [ ] Настроить авторизацию в `on_start`
- [ ] Реализовать проверку threshold'ов в `@events.quitting`

### k8s
- [ ] Реализовать `k8s_client.py`
- [ ] Заполнить список сервисов в `test_smoke.py`
- [ ] Настроить kubeconfig в CI через secrets

### crossbrowser
- [ ] Реализовать `get_driver` в `grid_client.py`
- [ ] Написать Page Objects или переиспользовать существующие
- [ ] Заполнить тесты в `test_ui.py`

### logs
- [ ] Реализовать `kibana_client.py` (Elasticsearch query DSL)
- [ ] Добавить фикстуру `test_run_window` в conftest.py
- [ ] Настроить index pattern под конкретный проект
