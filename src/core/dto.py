from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from enum import Enum


# =====================================================================================================================
# ============================================ Пользователи ===========================================================
# =====================================================================================================================

class UserStatus(Enum):
	ACTIVE = "Активен"
	EXPIRED = "Просрочен"
	BLOCKED = "Заблокирован"


class UserAddDTO(BaseModel):
	id: int
	name: str
	billing_start_date: date
	billing_end_date: date
	blocked: bool

	model_config = ConfigDict(from_attributes=True)

	@property
	def status(self):
		if self.blocked:
			return UserStatus.BLOCKED
		elif self.billing_end_date >= date.today():
			return UserStatus.ACTIVE
		else:
			return UserStatus.EXPIRED


class UserDTO(UserAddDTO):
	pass


class UserUpdateDTO(BaseModel):
	id: int | None = None
	name: str | None = None
	billing_start_date: date | None = None
	billing_end_date: date | None = None
	blocked: bool | None = None

	model_config = ConfigDict(from_attributes=True)


# =====================================================================================================================
# ============================================= Транзакции ============================================================
# =====================================================================================================================


class TransactionAddDTO(BaseModel):
	user_id: int
	amount: int
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)

class TransactionDTO(TransactionAddDTO):
	id: int


class TransactionUpdateDTO(BaseModel):
	user_id: int | None = None
	amount: int | None = None
	created_at: datetime | None = None
	updated_at: datetime | None = None

	model_config = ConfigDict(from_attributes=True)


# =====================================================================================================================
# ============================================ Сообщения ============================================================
# =====================================================================================================================


class MessageStatus(Enum):
	PENDING = "Ожидает отправки"
	SENT = "Отправлено"
	BOT_BLOCKED = "Бот заблокирован"
	CHAT_NOT_EXIST = "Чат не существует"
	ERROR = "Ошибка отправки"


class MessageAddDTO(BaseModel):
	recipient: int
	text: int
	status: Enum
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class MessageDTO(MessageAddDTO):
	id: int


class MessageUpdateDTO(BaseModel):
	recipient: int | None = None
	text: int | None = None
	status: Enum | None = None
	created_at: datetime | None = None
	updated_at: datetime | None = None

	model_config = ConfigDict(from_attributes=True)


# =====================================================================================================================
# ============================================ Регистрация ============================================================
# =====================================================================================================================


class RegistrationAddDTO(BaseModel):
	id: int
	name: str

	model_config = ConfigDict(from_attributes=True)


class RegistrationDTO(RegistrationAddDTO):
	pass


class RegistrationUpdateDTO(BaseModel):
	id: int | None = None
	name: str | None = None

	model_config = ConfigDict(from_attributes=True)