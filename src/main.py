from asyncio import run
from logger import log
from dto import UserDTO
from database import init_db
from repositories import user_repo
from src.dto import UserUpdateDTO
from datetime import date

user1 = UserDTO(id=123456, name="Test User 1")
user2 = UserDTO(id=56546268, name="Test User 2")

async def main():
	log.debug("Запуск")

	await init_db()

	await user_repo.add(user1)
	await user_repo.add(user2)

	users = await user_repo.get_all()
	print(users)
	updated_user = UserUpdateDTO(name="User 2 Updated", billing_end_date=date(2025, 12, 11), blocked=True)
	user = await user_repo.update(56546268, updated_user)
	print(user)
	users = await user_repo.get_all()
	print(users)
	await user_repo.delete(56546268)
	users = await user_repo.get_all()
	print(users)



if __name__ == "__main__":
	run(main())