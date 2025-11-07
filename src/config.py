from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from logger import log


class Settings(BaseSettings):
	log.debug("Инициализация настроек")

	# Общие настройки
	APP_NAME: str = Field(description="Название приложения")
	APP_VERSION: str = Field(description="Версия приложения")

	# Database
	DB_PATH: str = Field(description="DSM-строка для доступа к базе данных")

	model_config = SettingsConfigDict(env_file=".env")

	@property
	def get_db_url(self):
		return f"sqlite+aiosqlite:///{self.DB_PATH}"

settings = Settings()