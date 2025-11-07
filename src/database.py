from logger import log
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from orm import Base

DB_URL = "sqlite+aiosqlite:///data.db"

engine = create_async_engine(DB_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
	log.debug(f"Инициализация базы данных: '{DB_URL}'")
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)


def connection(method):
	async def wrapper(*args, **kwargs):
		async with async_session() as new_session:
			try:
				# Явно не открываем транзакции, так как они уже есть в контексте
				return await method(*args, session=new_session, **kwargs)

			except Exception as e:
				await new_session.rollback()  # Откатываем сессию при ошибке
				raise e  # Поднимаем исключение дальше
			finally:
				await new_session.close()

	return wrapper