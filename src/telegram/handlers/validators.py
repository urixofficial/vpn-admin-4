from src.db.repositories import AbstractRepository
from src.telegram.interface import ID_INVALID

async def new_id_valid(repo: AbstractRepository, item_id: str) -> tuple[bool, str]:
	if not item_id.isdigit():
		return False, "ID не является целым числом."
	id_int = int(item_id)
	if id_int <= 0:
		return False, "ID меньше или равен нулю."
	if await repo.get_by_id(id_int):
		return False, "Запись с таким ID уже существует."
	return True, ""

async def existing_id_valid(repo: AbstractRepository, item_id: str) -> tuple[bool, str]:
	if not item_id.isdigit():
		return False, "ID не является целым числом."
	id_int = int(item_id)
	if id_int <= 0:
		return False, "ID меньше или равен нулю."
	if not await repo.get_by_id(id_int):
		return False, "Запись с таким ID не найдена."
	return True, ""