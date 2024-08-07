import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, select
from datetime import datetime

from messages import logger

Base = declarative_base()

class IPDomainMapping(Base):
    __tablename__ = 'ip_domain_mappings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip_address = Column(String, nullable=False)
    host_name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)

class IPDomainDatabaseAsync:
    def __init__(self, db_path='sqlite+aiosqlite:///data/ip_domains.db'):
        self.engine = create_async_engine(db_path, echo=False, future=True)
        self.AsyncSession = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init(self):
        await self.setup_database()

    async def setup_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_data(self, data):
        """
        Асинхронное сохранение данных в базу данных.
        :param data: Словарь с IP-адресами и соответствующими доменами
        """
        async with self.AsyncSession() as session:
            async with session.begin():
                for ip_address, domain_list in data.items():
                    for domain in domain_list:
                        mapping = IPDomainMapping(
                            ip_address=ip_address,
                            host_name=domain['host_name'],
                            date=datetime.utcfromtimestamp(domain['date'])
                        )
                        session.add(mapping)
                await session.commit()

    async def get_latest_dates(self, ip_addresses, if_not_data=False):
        """
        Асинхронное извлечение самой последней даты для каждого IP-адреса из списка.
        :param ip_addresses: Список IP-адресов
        :return: Словарь с последней датой для каждого IP-адреса или False, если данных нет
        """
        async with self.AsyncSession() as session:
            latest_dates = {}
            for ip_address in ip_addresses:
                # Запрос на извлечение максимальной даты для текущего IP-адреса
                result = await session.execute(
                    select(func.max(IPDomainMapping.date)).where(IPDomainMapping.ip_address == ip_address)
                )
                latest_date = result.scalar()
                # Если данных нет, возвращаем False
                if latest_date is None:
                    latest_dates[ip_address] = if_not_data
                else:
                    # Конвертируем datetime в Unix timestamp
                    latest_dates[ip_address] = int(latest_date.timestamp())

            return latest_dates

    async def filter_new_domains(self, transformdata):
        """
        Filters the domains that are not already in the database with the same IP address.
        :param transformdata: Dictionary containing IP addresses and their associated domains.
        :return: Filtered dictionary containing only new entries.
        """
        async with self.AsyncSession() as session:
            filtered_data = {}
            existing_count = 0
            for ip_address, entries in transformdata.items():
                for entry in entries:
                    host_name = entry['host_name']
                    result = await session.execute(
                        select(IPDomainMapping).filter_by(ip_address=ip_address, host_name=host_name)
                    )
                    existing_entry = result.scalar()

                    if not existing_entry:
                        if ip_address not in filtered_data:
                            filtered_data[ip_address] = []
                        filtered_data[ip_address].append(entry)
                    else:
                        existing_count += 1
            logger.info(f"Existing entries in DB: {existing_count}")
            logger.info(f"New entries to be added: {sum(len(entries) for entries in filtered_data.values())}")
            return filtered_data

# Пример использования
async def main():
    db = IPDomainDatabaseAsync()
    await db.init()
    processed_data = {
        "89.108.65.169": [
            {
                "date": 1722056400,
                "host_name": "vernadskogo-circus.online",
                "ip_address": "89.108.65.169"
            },
            {
                "date": 1723056400,
                "host_name": "example.com",
                "ip_address": "89.108.65.169"
            }
        ],
        "91.239.26.147": [
            {
                "date": 1723056400,
                "host_name": "dommusic-kassa.ru",
                "ip_address": "91.239.26.147"
            }
        ]
    }

    await db.save_data(processed_data)

    domains = ["vernadskogo-circus.online", "nonexistentdomain.com", "example.com"]
    ip_results = await db.find_ip_by_domains(domains)
    for domain, ip in ip_results.items():
        if ip:
            print(f"Домен {domain} принадлежит IP {ip}")
        else:
            print(f"Домен {domain} не найден в базе")

    ip_addresses = [
        "89.108.65.169",
        "94.103.183.76"
    ]

    # Получаем последние даты для каждого IP-адреса
    latest_dates = await db.get_latest_dates(ip_addresses)
    for ip, date in latest_dates.items():
        if date:
            print(f"IP: {ip}, Последняя дата: {date}")
        else:
            print(f"IP: {ip}, Данных нет")

if __name__ == "__main__":
    asyncio.run(main())
