import asyncio
from datetime import datetime

import vt


class Request:
    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self.ip_addresses = dict()
        self.responses = dict()
        self.limits = {'per_minute': 4,
                       'in_a_day': 500}
        self.requests_made_today = 0

    def add_ip_address(self, ip_address, last_check_time=None):
        self.ip_addresses.setdefault(ip_address, last_check_time)

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


    async def fetch_domains_by_ip_addresses(self, ip_address_data):
        """
        Основная функция для получения доменов по IP-адресам.
        :param ip_address_data: Словарь с IP-адресами и датами последней записи или False
        :return: Словарь, где ключи — IP-адреса, а значения — списки доменов
        """
        self.update_ip_addresses(ip_address_data)
        await self.fetch_all_resolutions()

        # Извлекаем домены
        domains_by_ip = {}
        for ip, data in self.responses.items():
            domains_by_ip[ip] = [entry['attributes']['host_name'] for entry in data]

        return domains_by_ip

    async def _get_ip_resolutions(self, client, ip_address, limit=40, cursor=None):
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        # Выполняем запрос
        file = await client.get_json_async(
            path=f'/ip_addresses/{ip_address}/resolutions',
            params=params
        )
        self.requests_made_today += 1  # Увеличиваем счетчик запросов
        return file

    async def fetch_all_resolutions(self):
        semaphore = asyncio.Semaphore(self.limits['per_minute'])
        async with vt.Client(self.API_KEY) as client:
            tasks = [
                self._fetch_ip_data(client, ip_address, semaphore)
                for ip_address in self.ip_addresses
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _fetch_ip_data(self, client, ip_address, semaphore):
        async with semaphore:
            last_check_time = self.ip_addresses[ip_address]
            cursor = None
            all_data = []
            while True:
                # # Проверяем дневной лимит перед выполнением запроса
                # if self.requests_made_today >= self.limits['in_a_day']:
                #     print("Достигнут дневной лимит запросов. Запросы будут продолжены завтра.")
                #     return
                try:
                    response = await self._get_ip_resolutions(client, ip_address, cursor=cursor)
                    all_data.extend(response['data'])
                    if 'next' in response['links']:
                        cursor = response['meta']['cursor']
                        if last_check_time:
                            last_check_timestamp = datetime.timestamp(datetime.fromtimestamp(last_check_time))
                            last_date_in_data = max(
                                int(item['attributes']['date']) for item in response['data']
                            )
                            if last_date_in_data < last_check_timestamp:
                                break
                    else:
                        break
                except Exception as e:
                    print(f"Ошибка при выполнении запроса для IP {ip_address}: {e}")
                else:
                    print(ip_address, len(response['data']))
                finally:
                    sleep_time = 60 / self.limits['per_minute']
                    await asyncio.sleep(sleep_time)

            self.responses[ip_address] = all_data

    def get_responses(self):
        return self.responses

# Example usage
async def main():
    from dotenv import load_dotenv
    import os
    load_dotenv()

    VT_API_KEY = os.getenv('VT_API_KEY')
    requester = Request(VT_API_KEY)
    requester.add_ip_address('89.108.65.169', None)
    #requester.add_ip_address('94.103.183.76', None)
    await requester.fetch_all_resolutions()
    responses = requester.get_responses()

    # Print the collected responses
    for ip, data in responses.items():
        print(f"IP: {ip}")
        for entry in data:
            print(entry)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())