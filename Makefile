# Makefile для управления проектом

.PHONY: help build up down logs shell test clean

# Показать помощь
help:
	@echo "Доступные команды:"
	@echo "  build     - Собрать Docker образы"
	@echo "  up        - Запустить все сервисы"
	@echo "  down      - Остановить все сервисы"
	@echo "  logs      - Показать логи всех сервисов"
	@echo "  shell     - Подключиться к контейнеру приложения"
	@echo "  test      - Запустить тесты"
	@echo "  clean     - Очистить Docker ресурсы"
	@echo "  db-shell  - Подключиться к базе данных experiments"
	@echo "  db-shell-knowledge - Подключиться к базе знаний"
	@echo "  redis-cli - Подключиться к Redis"

# Собрать образы
build:
	docker-compose build

# Запустить все сервисы
up:
	docker-compose up -d

# Остановить все сервисы
down:
	docker-compose down

# Показать логи
logs:
	docker-compose logs -f

# Подключиться к контейнеру приложения
shell:
	docker-compose exec app bash

# Запустить тесты
test:
	docker-compose exec app python -m pytest

# Очистить Docker ресурсы
clean:
	docker-compose down -v
	docker system prune -f

# Подключиться к базе данных experiments
db-shell:
	docker-compose exec experiments_db psql -U postgres -d experiments_db

# Подключиться к базе знаний
db-shell-knowledge:
	docker-compose exec knowledge_db psql -U postgres -d knowledge_db

# Подключиться к Redis
redis-cli:
	docker-compose exec redis redis-cli

# Перезапустить приложение
restart-app:
	docker-compose restart app

# Показать статус сервисов
status:
	docker-compose ps
