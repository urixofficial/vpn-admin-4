from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from src.core.config import settings
from src.core.logger import log
from src.telegram.handlers import user_router, admin_router
from src.telegram.handlers.billing_handler import billing_crud
from src.telegram.handlers.user_handler import user_crud


class TelegramBot:
	def __init__(self):
		log.debug("Инициализация Telegram-бота")
		self.bot = Bot(token=settings.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
		self.dp = Dispatcher(storage=MemoryStorage())
		self.admin_id = settings.TELEGRAM_ADMIN_ID

		self._register_handlers()

	def _register_handlers(self):

		self.dp.include_router(admin_router)
		self.dp.include_router(user_crud.router)
		self.dp.include_router(billing_crud.router)
		self.dp.include_router(user_router)

	async def start_polling(self):
		log.info("Запуск Telegram-бота в режиме polling...")
		await self.dp.start_polling(self.bot)


telegram_bot = TelegramBot()
