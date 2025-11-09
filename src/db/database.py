from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.core.logger import log
from src.core.config import settings

from src.db.orm import Base


engine = create_async_engine(settings.get_db_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
	log.debug(f"Инициализация базы данных: '{settings.DB_PATH}'")
	try:
		async with engine.begin() as conn:
			# await conn.run_sync(Base.metadata.drop_all)
			await conn.run_sync(Base.metadata.create_all)
		log.debug("OK")
	except Exception as e:
		log.error(f"Ошибка: {e}")


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