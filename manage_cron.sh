#!/bin/bash

# Скрипт для управления заданиями cron

usage() {
    echo "Использование: $0 {add|remove|list} [время]"
    echo "  add [время]  - Добавить задание cron на указанное время (формат: ЧЧ:ММ)"
    echo "  remove       - Удалить все задания cron"
    echo "  list         - Показать текущие задания cron"
    exit 1
}

add_cron_job() {
    local time="$1"
    local hour="${time%:*}"
    local minute="${time#*:}"

    # Проверка, что время в правильном формате
    if ! [[ "$hour" =~ ^([01]?[0-9]|2[0-3])$ ]] || ! [[ "$minute" =~ ^([0-5]?[0-9])$ ]]; then
        echo "Ошибка: неверный формат времени. Используйте формат ЧЧ:ММ, где ЧЧ от 00 до 23, а ММ от 00 до 59."
        exit 1
    fi

    echo "Добавление задания cron на $time..."
    (crontab -l 2>/dev/null; echo "$minute $hour * * * cd $(pwd) && $(pwd)/.venv/bin/python $(pwd)/main.py >> $(pwd)/cron.log 2>&1") | crontab -
    echo "Задание cron добавлено: запуск скрипта в $time."
}

if [ "$1" == "add" ]; then
    if [ -z "$2" ]; then
        echo "Ошибка: укажите время для добавления задания cron (формат: ЧЧ:ММ)"
        exit 1
    fi
    add_cron_job "$2"
elif [ "$1" == "remove" ]; then
    echo "Удаление всех заданий cron..."
    crontab -r
    echo "Все задания cron удалены."
elif [ "$1" == "list" ]; then
    echo "Текущие задания cron:"
    crontab -l
else
    usage
fi
