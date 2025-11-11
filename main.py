from asyncio import run

from src.core.config import settings
from src.core.logger import log

from src.db.database import init_db
from src.telegram.bot import telegram_bot


async def main():
	log.info(f"Запуск {settings.APP_NAME} v{settings.APP_VERSION}")

	# Инициализация БД
	await init_db()

	# Запуск Telegram-бота
	await telegram_bot.start_polling()

if __name__ == "__main__":
	run(main())