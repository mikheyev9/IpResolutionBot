import asyncio
import os
import json
from dotenv import load_dotenv

from data import (read_ip_addresses,
                  transform_ip_resolutions,
                  save_data_as_json)
from data.database_manager import IPDomainDatabaseAsync
from request import Request
from messages import generate_telegram_messages, logger
from tg import TelegramBot

load_dotenv()
# Установить рабочую директорию в директорию, где находится скрипт
DEBUG = False
VT_API_KEY = os.getenv('VT_API_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_INFO')

request = Request(VT_API_KEY)
DB = IPDomainDatabaseAsync()
async def main():
    await DB.init()

    ip_addresses: list = await read_ip_addresses()
    ip_addresses = await DB.get_latest_dates(ip_addresses, if_not_data=1723056400)
    logger.info(f'Checking this {ip_addresses}')

    ip_resolutions = await request.fetch_domains_by_ip_addresses(ip_addresses)
    transform_ip_resolutions_ = transform_ip_resolutions(ip_resolutions)
    new_domains = await DB.filter_new_domains(transform_ip_resolutions_)

    if DEBUG:
        await save_data_as_json(transform_ip_resolutions_, new_domains)
    await DB.save_data(new_domains)

    messages = generate_telegram_messages(new_domains)
    async with TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID) as bot:
        await bot.add_messages_to_queue(messages)

if __name__ == "__main__":
    asyncio.run(main())
