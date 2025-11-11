from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from enum import Enum


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