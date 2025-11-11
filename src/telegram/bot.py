from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.core.config import settings
from src.core.logger import log
from src.telegram.handlers import user_router, admin_router, user_control_router, billing_control_router


class TelegramBot:
	def __init__(self):
		log.debug("Инициализация Telegram-бота")
		self.bot = Bot(token=settings.TELEGRAM_TOKEN)
		self.dp = Dispatcher(storage=MemoryStorage())
		self.admin_id = settings.TELEGRAM_ADMIN_ID

		self._register_handlers()

	def _register_handlers(self):

		self.dp.include_router(admin_router)
		self.dp.include_router(user_control_router)
		self.dp.include_router(billing_control_router)
		self.dp.include_router(user_router)

	async def start_polling(self):
		log.info("Запуск Telegram-бота в режиме polling...")
		await self.dp.start_polling(self.bot)


telegram_bot = TelegramBot()
