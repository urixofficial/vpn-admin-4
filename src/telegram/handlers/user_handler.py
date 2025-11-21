# src/telegram/user_crud.py
from src.telegram.handlers.crud_handler import BaseCRUDHandler
from src.db.repositories import user_repo, AbstractRepository
from src.core.dto import UserAddDTO, UserDTO, UserStatus
from src.telegram.keyboards import to_user_control_keyboard, user_profile_keyboard
from src.telegram.interface import (
	USER_LIST_HEADER, USER_LIST_ROW, USER_PROFILE_TEMPLATE,
	ENTER_USER_ID, ENTER_USER_NAME, USER_LIST_STATUS_ACTIVE, USER_LIST_STATUS_INACTIVE, ID_INVALID,
	NAME_INVALID
)

class UserCRUDHandler(BaseCRUDHandler[UserAddDTO, UserDTO, AbstractRepository]):
	entity_name = "user"
	repo = user_repo
	add_dto_class = UserAddDTO
	dto_class = UserDTO

	list_header = USER_LIST_HEADER
	list_row_template = USER_LIST_ROW
	profile_template = USER_PROFILE_TEMPLATE
	back_keyboard = to_user_control_keyboard()
	profile_keyboard = user_profile_keyboard()

	add_fields = ["id", "name"]
	field_prompts = {
		"id": ENTER_USER_ID,
		"name": ENTER_USER_NAME
	}
	field_validators = {
		"id": lambda x: (x.isdigit() and x > 0, ID_INVALID),
		"name": lambda x: (len(x) > 2, NAME_INVALID) if len(x) == 0 else (len(x) <= 25, NAME_INVALID)
	}

	def get_entity_id(self, item: UserDTO) -> int:
		return item.id

	def format_list_row(self, item: UserDTO) -> str:
		status = USER_LIST_STATUS_ACTIVE if item.status == UserStatus.ACTIVE else USER_LIST_STATUS_INACTIVE
		return self.list_row_template.format(status=status, name=item.name, user_id=item.id)

	async def resolve_field_value(self, field: str, value: str):
		if field == "id":
			return int(value)
		return value

# Создаём экземпляр
user_crud = UserCRUDHandler()