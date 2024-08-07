import asyncio
from aiogram import Bot, Dispatcher, html
from aiogram.exceptions import TelegramRetryAfter, TelegramAPIError
from contextlib import asynccontextmanager


class TelegramBot:
    def __init__(self, token, channel_id, initial_delay=1):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.channel_id = channel_id
        self.message_queue: asyncio.Queue[str] = asyncio.Queue()
        self.delay = initial_delay

    async def send_message(self, message):
        try:
            await self.bot.send_message(chat_id=self.channel_id, text=html.quote(message))
            self.delay = 1  # Сброс задержки после успешной отправки
        except TelegramRetryAfter as e:
            # Слишком много запросов, необходимо подождать
            self.delay = e.retry_after + 2
            await self.message_queue.put(message)  # Повторно добавить сообщение в очередь
        except TelegramAPIError:
            # Другие API ошибки
            await self.message_queue.put(message)  # Повторно добавить сообщение в очередь

    async def process_queue(self):
        while True:
            message = await self.message_queue.get()
            await self.send_message(message)
            await asyncio.sleep(self.delay)
            self.message_queue.task_done()

    async def add_to_queue(self, message: str):
        await self.message_queue.put(message)

    async def add_messages_to_queue(self, messages: list):
        for message in messages:
            await self.add_to_queue(message)

    async def start_polling(self):
        asyncio.create_task(self.process_queue())
        await self.dp.start_polling(self.bot)

    async def wait_until_done(self):
        await self.message_queue.join()

    async def close(self):
        await self.bot.session.close()

    async def __aenter__(self):
        asyncio.create_task(self.process_queue())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.wait_until_done()
        await self.close()


async def main():
    from dotenv import load_dotenv
    import os
    load_dotenv()

    token = os.getenv('TELEGRAM_BOT_API_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_INFO')

    async with TelegramBot(token, channel_id) as bot:
        # Пример добавления одного сообщения в очередь
        await bot.add_to_queue("Новое доменное имя: example.com")
        # Пример добавления списка сообщений в очередь
        messages = [
            "Новое доменное имя: example1.com",
            "Новое доменное имя: example2.com",
            "Новое доменное имя: example3.com"
        ]
        await bot.add_messages_to_queue(messages)

if __name__ == "__main__":
    asyncio.run(main())