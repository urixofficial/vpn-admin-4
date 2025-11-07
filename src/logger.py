import sys
from loguru import logger

LOG_LEVEL = "DEBUG"
LOG_PATH = "logs/app.log"
LOG_ROTATION = "1 MB"
LOG_RETENTION = "10 days"

def setup_logging():
	"""Настройка системы логирования"""

	# Удаляем стандартный обработчик
	logger.remove()

	# Консольный вывод
	logger.add(
		sys.stdout,
		level=LOG_LEVEL,
		format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
		       "<level>{level: <8}</level> | "
		       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
		       "<level>{message}</level>",
		colorize=True
	)

	# Файловый вывод
	logger.add(
		LOG_PATH,
		level=LOG_LEVEL,
		format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
		rotation=LOG_ROTATION,
		retention=LOG_RETENTION,
		compression="zip"
	)

	logger.info(f"Логирование инициализировано. Уровень: {LOG_LEVEL}")
	return logger


# Глобальный экземпляр логгера
log = setup_logging()