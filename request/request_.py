import asyncio
from datetime import datetime

import vt

from messages import logger

def get_max_and_min_dates(data):
    first_date_in_data = min(
        int(item['attributes']['date']) for item in data
    )
    last_date_in_data = max(
        int(item['attributes']['date']) for item in data
    )
    min_date = datetime.utcfromtimestamp(first_date_in_data).strftime('%Y-%m-%d %H:%M:%S')
    max_date = datetime.utcfromtimestamp(last_date_in_data).strftime('%Y-%m-%d %H:%M:%S')
    return min_date, max_date, last_date_in_data

class Request:
    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self.ip_addresses = dict()
        self.responses = dict()
        self.limits = {'per_minute': 4, 'in_a_day': 500}
        self.sleep_time = 60 / self.limits['per_minute']
        self.requests_made_today = 0

    def update_ip_addresses(self, ip_address_data):
        """
        Обновляет словарь IP-адресов и их временных меток.
        :param ip_address_data: Словарь с IP-адресами и датами последней записи или False
        """
        for ip_address, last_check_time in ip_address_data.items():
            if last_check_time is False:
                self.ip_addresses[ip_address] = None
            else:
                self.ip_addresses[ip_address] = last_check_time

    async def _get_ip_resolutions(self, client, ip_address, limit=40, cursor=None):
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        file = await client.get_json_async(
            path=f'/ip_addresses/{ip_address}/resolutions',
            params=params
        )
        self.requests_made_today += 1
        return file

    async def fetch_all_resolutions(self):
        """
        Запрашивает разрешения для всех IP-адресов.
        :return: Словарь с данными для каждого IP-адреса
        """
        semaphore = asyncio.Semaphore(self.limits['per_minute'])
        async with vt.Client(self.API_KEY) as client:
            tasks = [
                self._fetch_ip_data(client, ip_address, semaphore)
                for ip_address in self.ip_addresses
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, tuple):
                ip_address, data = result
                self.responses[ip_address] = data
        return self.responses

    async def _fetch_ip_data(self, client, ip_address, semaphore):
        error_counter = 3
        async with (semaphore):
            last_check_time = self.ip_addresses[ip_address]
            cursor = None
            all_data = []
            while True:
                try:
                    response = await self._get_ip_resolutions(client, ip_address, cursor=cursor)
                    all_data.extend(response['data'])
                    (min_date_in_data,
                     max_date_in_data,
                     max_date_in_data_iso) = get_max_and_min_dates(response['data'])
                    if 'next' in response['links']:
                        cursor = response['meta']['cursor']
                        if last_check_time:
                            if max_date_in_data_iso < last_check_time:
                                break
                    else:
                        break
                except Exception as e:
                    error_counter -= 1
                    logger.error(f"Ошибка при выполнении запроса для IP {ip_address}: {e}")
                    if not error_counter:
                        return ip_address, all_data
                else:
                    logger.info(f"{ip_address} "
                                f"min_date:{min_date_in_data}, max_date:{max_date_in_data} "
                                f"response len:{len(response['data'])}")
                finally:
                    await asyncio.sleep(self.sleep_time)

            return ip_address, all_data

    async def fetch_domains_by_ip_addresses(self, ip_address_data):
        """
        Основная функция для получения данных по IP-адресам.
        :param ip_address_data: Словарь с IP-адресами и датами последней записи или False
        :return: Словарь, где ключи — IP-адреса, а значения — полные данные
        """
        self.update_ip_addresses(ip_address_data)
        responses = await self.fetch_all_resolutions()
        return responses

# Пример использования
async def main():
    from dotenv import load_dotenv
    import os
    load_dotenv()

    VT_API_KEY = os.getenv('VT_API_KEY')
    request = Request(VT_API_KEY)

    # Пример данных для ввода
    ip_address_data = {
        '89.108.65.169': 1722056400,
        '203.0.113.42': 1723056400
    }

    # Получаем полные данные по IP-адресам
    responses = await request.fetch_domains_by_ip_addresses(ip_address_data)
    for ip, data in responses.items():
        print(f"IP: {ip}, Данные: {data}")


# Запуск асинхронной функции main
if __name__ == "__main__":
    asyncio.run(main())