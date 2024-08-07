import aiofiles
import json

def transform_ip_resolutions(ip_resolutions):
    """
    Преобразует данные о разрешениях IP в удобный формат.
    :param ip_resolutions: Словарь, где ключ — IP-адрес, а значение — список данных о доменах
    :return: Новый словарь с ключами IP-адресов и значениями списков словарей с 'date', 'host_name' и 'ip_address'
    """
    transformed_data = {}
    for ip_address, resolutions in ip_resolutions.items():
        transformed_data[ip_address] = []
        for resolution in resolutions:
            # Извлекаем необходимые данные
            attributes = resolution.get('attributes', {})
            host_name = attributes.get('host_name')
            date = attributes.get('date')

            transformed_data[ip_address].append({
                'ip_address': ip_address,
                'host_name': host_name,
                'date': date
            })
    return transformed_data


async def read_ip_addresses(file_path='data/ip_addresses.json'):
    """
    Асинхронно читает IP-адреса из JSON-файла.
    :param file_path: Путь к JSON-файлу
    :return: Список IP-адресов
    """
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
        contents = await file.read()
        ip_addresses = json.loads(contents)
    return ip_addresses

async def main():
    file_path = 'ip_addresses.json'
    ip_addresses = await read_ip_addresses(file_path)
    print(f"Извлеченные IP-адреса: {ip_addresses}")

async def save_data_as_json(transform_ip_resolutions_, new_domains):
    # Сохранение transformdata
    async with aiofiles.open('data/example_data/transform_ip_resolutions_.json', 'w', encoding='utf-8') as outfile:
        await outfile.write(json.dumps(transform_ip_resolutions_, indent=4))

    # Сохранение new_domains
    async with aiofiles.open('data/example_data/new_domains.json', 'w', encoding='utf-8') as outfile:
        await outfile.write(json.dumps(new_domains, indent=4))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
