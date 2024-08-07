from datetime import datetime


def generate_telegram_messages(new_domains):
    """
    Генерирует сообщения для Telegram из структуры данных new_domains.

    :param new_domains: Словарь с данными о доменах
    :return: Список сообщений для отправки в Telegram
    """
    messages = []
    info_link = "https://www.virustotal.com/gui/home/url"
    link_description = f"Детальная информация на: {info_link}"

    for ip_address, domains in new_domains.items():
        # Заголовок с выразительным значком для каждого IP-адреса
        message_lines = [f"🔹 Новые домены для IP {ip_address}:"]

        for domain_info in domains:
            host_name = domain_info['host_name']
            # Преобразуем дату из UNIX timestamp в формат YYYY-MM-DD
            date = datetime.utcfromtimestamp(domain_info['date']).strftime('%Y-%m-%d')
            # Формируем строку с разделителями
            message_line = f"{host_name} ➖ {date}"
            message_lines.append(message_line)

        # Добавляем описание с ссылкой в конец сообщения
        message_lines.append(link_description)

        # Создаем сообщение для текущего IP-адреса
        current_message = "\n".join(message_lines)

        # Если сообщение слишком длинное, разбиваем его
        if len(current_message) > 4000:
            current_message_parts = []
            part = []
            for line in message_lines:
                if sum(len(p) for p in part) + len(line) + 1 > 4000:  # +1 для новой строки
                    # Добавляем ссылку в конец каждой части
                    part.append(link_description)
                    current_message_parts.append("\n".join(part))
                    part = [line]
                else:
                    part.append(line)
            if part:
                part.append(link_description)  # Добавляем ссылку в последнюю часть
                current_message_parts.append("\n".join(part))
            messages.extend(current_message_parts)
        else:
            messages.append(current_message)

    return messages

if __name__ == '__main__':
    # Пример использования
    new_domains = {
        "89.108.65.169": [
            {
                "ip_address": "89.108.65.169",
                "host_name": "vernadskogo-circus.online",
                "date": 1722056400
            },
            {
                "ip_address": "89.108.65.169",
                "host_name": "nikulina-circus.online",
                "date": 1721888877
            }
        ]
    }

    messages = generate_telegram_messages(new_domains)
    for message in messages:
        print(message)
