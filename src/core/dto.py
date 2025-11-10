from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from enum import Enum


class UserStatus(Enum):
	ACTIVE = "Активен"
	EXPIRED = "Просрочен"
	BLOCKED = "Заблокирован"

class UserDTO(BaseModel):
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


class UserUpdateDTO(BaseModel):
	id: int | None = None
	name: str | None = None
	billing_start_date: date | None = None
	billing_end_date: date | None = None
	blocked: bool | None = None

	model_config = ConfigDict(from_attributes=True)


class TransactionDTO(BaseModel):
	id: int
	user_id: int
	amount: int
	created: datetime
	updated: datetime

	model_config = ConfigDict(from_attributes=True)


class TransactionUpdateDTO(BaseModel):
	user_id: int | None = None
	amount: int | None = None
	created: datetime | None = None
	updated: datetime | None = None

	model_config = ConfigDict(from_attributes=True)