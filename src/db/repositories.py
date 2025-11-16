from typing import TypeVar, Generic, Type, List
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from datetime import date
from dateutil.relativedelta import relativedelta

from src.core.logger import log

from src.db.database import connection
from src.core.dto import (UserAddDTO, UserDTO, UserUpdateDTO, TransactionAddDTO, TransactionDTO, TransactionUpdateDTO,
                          RegistrationAddDTO, RegistrationDTO, RegistrationUpdateDTO, MessageAddDTO, MessageDTO,
                          MessageUpdateDTO)
from src.db.orm import Base, UserORM, TransactionORM, RegistrationORM, MessageORM

AddDTO = TypeVar('AddDTO', bound=BaseModel)
DTO = TypeVar('DTO', bound=BaseModel)
DTOUpdate = TypeVar('DTOUpdate', bound=BaseModel)
ORM = TypeVar('ORM', bound=Base)


class AbstractRepository(Generic[AddDTO, DTO, ORM, DTOUpdate]):
	def __init__(self, add_dto_model: Type[DTO], dto_model: Type[DTO], update_dto_model: Type[DTOUpdate], orm_model: Type[ORM]):
		self.add_dto_model = add_dto_model
		self.dto_model = dto_model
		self.update_dto_model = update_dto_model
		self.orm_model = orm_model


	@connection
	async def add(self, dto: AddDTO, session: AsyncSession) -> int | None:
		log.debug(f"Добавление записи: '{dto}' в таблицу '{self.orm_model.__tablename__}'")
		try:
			orm_instance = self.orm_model(**dto.model_dump())
			session.add(orm_instance)
			await session.flush()  # Получаем ID без коммита
			await session.commit()
			log.debug(f"OK, ID: {orm_instance.id}")
			return orm_instance.id
		except IntegrityError:
			log.error(f"Ошибка: запись с таким ключом уже существует")
			return None
		except Exception as e:
			log.error(f"Ошибка: {e}")
			return None

	@connection
	async def update(self, record_id: int, update_dto: DTOUpdate, session: AsyncSession) -> bool:
		log.debug(f"Обновление записи {record_id}: в таблице '{self.orm_model.__tablename__}'")
		try:
			orm_object = await session.get(self.orm_model, record_id)
			update_data = update_dto.model_dump(exclude_unset=True)
			for key, value in update_data.items():
				setattr(orm_object, key, value)
			await session.commit()
			await session.refresh(orm_object)
			log.debug("OK")
			return True
		except NoResultFound:
			log.error(f"Запись {record_id} не найдена")
			return False
		except Exception as e:
			log.error(f"Ошибка: {e}")
			return False

	@connection
	async def delete(self, record_id: int, session: AsyncSession) -> bool:
		try:
			log.debug(f"Удаление записи {record_id} из таблицы: '{self.orm_model.__tablename__}'")
			query = delete(self.orm_model).where(self.orm_model.id == record_id)
			result = await session.execute(query)
			await session.commit()
			log.debug("OK")
			return result.rowcount > 0
		except Exception as e:
			log.error(f"Ошибка: {e}")
			return False

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
		log.debug(f"Получение записи '{record_id} из таблицы '{self.orm_model.__tablename__}'")
		orm_object = await session.get(self.orm_model, record_id)
		if not orm_object:
			return None
		dto_object = self.dto_model.model_validate(orm_object)
		return dto_object


class UserRepository(AbstractRepository[UserAddDTO, UserDTO, UserUpdateDTO, UserORM]):
	def __init__(self):
		super().__init__(UserAddDTO, UserDTO, UserUpdateDTO, UserORM)


class BillingRepository(AbstractRepository[TransactionAddDTO, TransactionDTO, TransactionUpdateDTO, TransactionORM]):
	def __init__(self):
		super().__init__(TransactionAddDTO, TransactionDTO, TransactionUpdateDTO, TransactionORM)

	@connection
	async def add(self, dto: TransactionAddDTO, session: AsyncSession) -> int | None:
		log.debug(f"Добавление транзакции: '{dto}' и обновление billing_end_date")
		try:
			# 1. Добавляем транзакцию
			orm_instance = TransactionORM(**dto.model_dump())
			session.add(orm_instance)
			await session.flush()

			# 2. Пересчитываем billing_end_date
			months_to_add = dto.amount // 100
			if months_to_add > 0:
				user = await session.get(UserORM, dto.user_id)
				if user:
					current_end = max(date.today(), user.billing_end_date)
					user.billing_end_date = current_end + relativedelta(months=months_to_add)
					log.debug(
						f"Продление подписки для {user.name}: +{months_to_add} мес. → {user.billing_end_date}")

			await session.commit()
			log.debug(f"OK, ID транзакции: {orm_instance.id}")
			return orm_instance.id

		except IntegrityError:
			await session.rollback()
			log.error("Ошибка: нарушение целостности данных")
			return None
		except Exception as e:
			await session.rollback()
			log.error(f"Ошибка: {e}")
			return None

	@connection
	async def delete(self, record_id: int, session: AsyncSession) -> bool:
		log.debug(f"Удаление транзакции {record_id} и пересчёт billing_end_date")
		try:
			# 1. Получаем транзакцию
			transaction = await session.get(TransactionORM, record_id)
			if not transaction:
				log.error(f"Транзакция {record_id} не найдена")
				return False

			user_id = transaction.user_id
			amount = transaction.amount
			months_to_subtract = amount // 100

			# 2. Удаляем транзакцию
			await session.delete(transaction)

			# 3. Пересчитываем billing_end_date
			if months_to_subtract > 0:
				# Перезагружаем пользователя
				user = await session.get(UserORM, user_id)
				if user:
					user.billing_end_date = user.billing_end_date - relativedelta(months=months_to_subtract)
					log.debug(
						f"Сокращение подписки для {user.name}: -{months_to_subtract} мес. → {user.billing_end_date}"
					)

			await session.commit()
			log.debug("OK")
			return True

		except Exception as e:
			await session.rollback()
			log.error(f"Ошибка: {e}")
			return False


class MessageRepository(AbstractRepository[MessageAddDTO, MessageDTO, MessageUpdateDTO, MessageORM]):
	def __init__(self):
		super().__init__(TransactionAddDTO, TransactionDTO, TransactionUpdateDTO, TransactionORM)


class RegistrationRepo(AbstractRepository[RegistrationAddDTO, RegistrationDTO, RegistrationUpdateDTO, RegistrationORM]):
	def __init__(self):
		super().__init__(RegistrationAddDTO, RegistrationDTO, RegistrationUpdateDTO, RegistrationORM)



user_repo = UserRepository()
billing_repo = BillingRepository()
messages_repo = MessageRepository()
registration_repo = RegistrationRepo()
