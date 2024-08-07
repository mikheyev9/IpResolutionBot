# MonitorWeb
Проект `MonitorWeb` предназначен для мониторинга и обработки данных с использованием API VirusTotal и отправки обновлений в Telegram.

### Требования

- Python 3.11
- Poetry
- Cron
### Установка

1) make install
2) make cron-add (добавляем время запуска скрпита)


###  Ручной запуск скрипта:
    make run

### Управление заданиями Cron

-  Добавить задание cron: make cron-add
- Показать текущие задания cron: make cron-list
- Запускает скрипт на указанное время (формат: ЧЧ:ММ):make cron-add
- Удалить все задания cron: make cron-remove





