# Настройка дашборда FastAPI Observability (ID 16110)

Пошаговая инструкция по настройке дашборда [FastAPI Observability](https://grafana.com/grafana/dashboards/16110-fastapi-observability/) для полной работы всех панелей.

## Что уже сделано в проекте

### 1. Метрики Prometheus (добавлены в приложение)

- `fastapi_app_info` — для переменной "Application Name"
- `fastapi_requests_total` — общее количество запросов
- `fastapi_responses_total` — ответы по status_code (2xx, 5xx и т.д.)
- `fastapi_exceptions_total` — необработанные исключения
- `fastapi_requests_in_progress` — запросы в обработке
- `fastapi_requests_duration_seconds` — гистограмма длительности (с buckets для P99)

### 2. Инфраструктура

- **Prometheus** — скрейпит `/metrics` приложения
- **Loki** — принимает логи
- **Promtail** — собирает логи Docker-контейнеров, парсит structlog JSON
- **Tempo** — трассировки OpenTelemetry
- **Grafana** — визуализация

---

## Шаг 1: Импорт дашборда

1. Откройте Grafana: http://localhost:3000
2. Войдите (admin / пароль из `.env` или по умолчанию `admin`)
3. Меню **Dashboards** → **Import**
4. В поле **Import via gnetId** введите: `16110`
5. Нажмите **Load**
6. Выберите:
   - **Prometheus** → ваш источник Prometheus (uid: `prometheus`)
   - **Loki** → ваш источник Loki (uid: `loki`)
7. Нажмите **Import**

---

## Шаг 2: Проверка переменных

1. В верхней части дашборда выберите **Application Name** → должно быть `Experiment Management API`
2. Если пусто — подождите 1–2 минуты (метрика `fastapi_app_info` должна появиться после перезапуска app)

---

## Шаг 3: Исправление Loki-запросов (логи)

Дашборд по умолчанию использует `compose_service=~"app-.*"`, а наш сервис называется `app`. Нужно поправить запросы.

### Панель "Log Type Rate"

1. Откройте дашборд в режиме редактирования (иконка карандаша)
2. Найдите панель **Log Type Rate**
3. В запросе замените:

   **Было:**
   ```
   sum by(type) (rate({compose_service=~"app-.*"} | pattern ` [<_>= <_>= <_>=] - ` | type != "" |= "$log_keyword" [1m]))
   ```

   **Стало:**
   ```
   sum by(level) (rate({compose_service=~"app.*", level=~".+"} |= "$log_keyword" [1m]))
   ```

4. Сохраните панель

### Панель "Log of All FastAPI App"

1. Найдите панель **Log of All FastAPI App**
2. В запросе замените:

   **Было:**
   ```
   {compose_service=~"app-.*"} | pattern ` [<_>= <_>= <_>=] - ` | line_format "{{.compose_service}}\t{{.type}}\t trace_id={{.trace_id}}\t {{.msg}}" |= "$log_keyword"
   ```

   **Стало:**
   ```
   {compose_service=~"app.*"} | line_format "{{.compose_service}}\t{{.level}}\t trace_id={{.trace_id}}\t {{.__line__}}" |= "$log_keyword"
   ```

3. Сохраните панель и дашборд

---

## Шаг 4: Перезапуск приложения

Чтобы новые метрики начали экспортироваться:

```bash
docker-compose restart app
```

Подождите 1–2 минуты, затем обновите дашборд (F5 или кнопка Refresh).

---

## Ожидаемый результат

| Панель | Источник | Статус после настройки |
|--------|----------|-------------------------|
| Total Requests | Prometheus | ✅ |
| Requests Count | Prometheus | ✅ |
| Requests Average Duration | Prometheus | ✅ |
| Total Exceptions | Prometheus | ✅ |
| Percent of 2xx Requests | Prometheus | ✅ |
| Percent of 5xx Requests | Prometheus | ✅ |
| PR 99 Requests Duration | Prometheus | ✅ |
| Request In Process | Prometheus | ✅ |
| Request Per Sec | Prometheus | ✅ |
| Log Type Rate | Loki | ✅ (после правки запроса) |
| Log of All FastAPI App | Loki | ✅ (после правки запроса) |

---

## Ссылки

- [Дашборд на Grafana.com](https://grafana.com/grafana/dashboards/16110-fastapi-observability/)
- [Репозиторий blueswen/fastapi-observability](https://github.com/blueswen/fastapi-observability) — эталонная реализация
- [Документация Grafana Loki LogQL](https://grafana.com/docs/loki/latest/logql/)
