# Makefile для управления окружением и cron с использованием Poetry

# Переменные
CRON_SCRIPT := ./manage_cron.sh

# Установка зависимостей и создание виртуального окружения с помощью Poetry
.PHONY: install
install:
	poetry install
	pre-commit install

# Запуск скрипта вручную
.PHONY: run
run:
	poetry run python main.py

# Проверка и установка прав на выполнение скрипта управления cron
.PHONY: permissions
permissions:
	@if [ ! -x "$(CRON_SCRIPT)" ]; then \
		echo "Установка прав на выполнение для $(CRON_SCRIPT)"; \
		chmod +x $(CRON_SCRIPT); \
	fi

# Добавление задания cron
.PHONY: cron-add
cron-add: permissions
	@read -p "Введите время для задания cron (формат ЧЧ:ММ): " time; \
	$(CRON_SCRIPT) add $$time

# Удаление всех заданий cron
.PHONY: cron-remove
cron-remove: permissions
	$(CRON_SCRIPT) remove

# Просмотр текущих заданий cron
.PHONY: cron-list
cron-list: permissions
	$(CRON_SCRIPT) list

# Обновление зависимостей
.PHONY: update
update:
	poetry update

# Запуск pre-commit hooks
.PHONY: pre-commit
pre-commit:
	pre-commit run --all-files

# Цель по умолчанию
.DEFAULT_GOAL := install
