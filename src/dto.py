from pydantic import BaseModel, ConfigDict
from datetime import date

class UserDTO(BaseModel):
	id: int
	name: str
	billing_start_date: date = date. today()
	billing_end_date: date = date.today()
	blocked: bool = False

	model_config = ConfigDict(from_attributes=True)

class UserUpdateDTO(BaseModel):
	id: int | None = None
	name: str | None = None
	billing_start_date: date | None = None
	billing_end_date: date | None = None
	blocked: bool | None = None

	model_config = ConfigDict(from_attributes=True)