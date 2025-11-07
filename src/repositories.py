from typing import TypeVar, Generic, Type, List

from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import connection
from dto import UserDTO, UserUpdateDTO
from logger import log
from orm import Base, UserORM

DTO = TypeVar('DTO', bound=BaseModel)
ORM = TypeVar('ORM', bound=Base)
DTOUpdate = TypeVar('DTOUpdate', bound=BaseModel)


class AbstractRepository(Generic[DTO, ORM, DTOUpdate]):
	def __init__(self, dto_model: Type[DTO], orm_model: Type[ORM], update_dto_model: Type[DTOUpdate]):
		self.dto_model = dto_model
		self.orm_model = orm_model
		self.update_dto_model = update_dto_model

	@connection
	async def add(self, dto: DTO, session: AsyncSession) -> None:
		log.debug(f"Добавление записи: '{dto}' в таблицу '{self.orm_model.__tablename__}'")
		orm_instance = self.orm_model(**dto.model_dump())
		session.add(orm_instance)
		await session.commit()

	@connection
	async def update(self, record_id: int, update_dto: DTOUpdate, session: AsyncSession) -> DTO | None:
		log.debug(f"Обновление записи с ID={record_id}: в таблице '{self.orm_model.__tablename__}'")
		# Получаем объект
		# query = select(self.orm_model).where(self.orm_model.id == record_id)
		# result = await session.execute(query)
		# orm_object = result.scalar_one_or_none()
		orm_object = await session.get_one(self.orm_model, record_id)
		if not orm_object:
			log.warning(f"Запись с ID={record_id} не найдена")
			return None

		# Обновляем только переданные поля
		update_data = update_dto.model_dump(exclude_unset=True)
		for key, value in update_data.items():
			setattr(orm_object, key, value)

		await session.commit()
		await session.refresh(orm_object)
		return self.dto_model.model_validate(orm_object)

	@connection
	async def delete(self, record_id: int, session: AsyncSession) -> bool:
		log.debug(f"Удаление записи c ID={record_id} из таблицы: '{self.orm_model.__tablename__}'")
		query = delete(self.orm_model).where(self.orm_model.id == record_id)
		result = await session.execute(query)
		await session.commit()
		return result.rowcount > 0

	@connection
	async def get_all(self, session: AsyncSession) -> List[DTO] | None:
		log.debug(f"Получение всех записей из таблицы: '{self.orm_model.__tablename__}'")
		query = select(self.orm_model)
		result = await session.execute(query)
		orm_objects = result.scalars().all()
		if not orm_objects:
			return None
		return [self.dto_model.model_validate(obj) for obj in orm_objects]

	@connection
	async def get_by_id(self, record_id: int, session: AsyncSession) -> DTO | None:
		log.debug(f"Получение записи с ID='{record_id} из таблицы '{self.orm_model.__tablename__}'")
		orm_object = await session.get(self.orm_model, record_id)
		if not orm_object:
			return None
		dto_object = self.dto_model.model_validate(orm_object)
		return dto_object


class UserRepository(AbstractRepository[UserDTO, UserORM, UserUpdateDTO]):
	def __init__(self):
		super().__init__(UserDTO, UserORM, UserUpdateDTO)


user_repo = UserRepository()
