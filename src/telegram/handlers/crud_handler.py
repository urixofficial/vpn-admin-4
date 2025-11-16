# src/telegram/crud_handler.py
from abc import ABC, abstractmethod
from typing import (
	Protocol,
	Generic,
	TypeVar,
	Callable,
	Any,
)

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from pydantic import BaseModel

from src.core.logger import log
from src.db.repositories import AbstractRepository
from src.telegram.keyboards import admin_cancel_keyboard, admin_confirmation_keyboard

AddDTO = TypeVar("AddDTO", bound=BaseModel)
DTO = TypeVar("DTO", bound=BaseModel)
RepoT = TypeVar("RepoT", bound=AbstractRepository)





class BaseCRUDHandler(Generic[AddDTO, DTO, RepoT], ABC):
	entity_name: str
	repo: RepoT
	add_dto_class: type[AddDTO]
	dto_class: type[DTO]

	# Настраиваемые шаблоны и клавиатуры
	list_header: str
	list_row_template: str
	profile_template: str
	back_keyboard: InlineKeyboardMarkup
	profile_keyboard: InlineKeyboardMarkup

	# Поля для добавления
	add_fields: list[str]
	field_prompts: dict[str, str]
	field_validators: dict[str, Callable[[str], tuple[bool, str | None]]]



	def __init__(self):

		class CRUDStates(StatesGroup):
			enter_show_id = State("enter_show_id", self.entity_name)
			enter_add_field = State("enter_add_field", self.entity_name)
			confirm_delete = State("enter_add_field", self.entity_name)

		self.states = CRUDStates()
		self.router = Router(name=f"{self.entity_name}_crud_router")
		self._register_handlers()

	# === Абстрактные методы (переопределяются при необходимости) ===
	@abstractmethod
	def get_entity_id(self, item: DTO) -> int:
		...

	@abstractmethod
	def format_list_row(self, item: DTO) -> str:
		...

	@abstractmethod
	async def resolve_field_value(self, field: str, value: str) -> Any:
		...

	# === Универсальная регистрация ===
	def _register_handlers(self):
		self._register_list()
		self._register_show()
		self._register_add()
		self._register_delete()

	# === Отображение профиля ===
	async def _show_profile(self, message: Message | CallbackQuery, item: DTO):
		log.debug(f"Вывод профиля {self.entity_name}. Отображение")

		text = self.profile_template.format(**item.__dict__)
		if isinstance(message, CallbackQuery):
			await message.message.edit_text(text, reply_markup=self.profile_keyboard)
			await message.answer()
		else:
			await message.answer(text, reply_markup=self.profile_keyboard)

	# === Список ===
	def _register_list(self):
		@self.router.callback_query(F.data == f"{self.entity_name}_list")
		async def list_cb(callback: CallbackQuery):
			log.debug(f"Вывод списка {self.entity_name}")

			items = await self.repo.get_all()
			if not items:
				await callback.message.edit_text(
					f"Список {self.entity_name} пуст", reply_markup=self.back_keyboard
				)
				await callback.answer()
				return

			text = self.list_header + "\n"
			for item in items:
				text += self.format_list_row(item) + "\n"

			await callback.message.edit_text(text, reply_markup=self.back_keyboard)
			await callback.answer()

	# === Показ профиля ===
	def _register_show(self):

		@self.router.callback_query(F.data == f"{self.entity_name}_show")
		async def show_start(callback: CallbackQuery, state: FSMContext):
			log.debug(f"Вывод профиля {self.entity_name.capitalize()}. Запрос ID")
			await state.clear()
			await callback.message.edit_text(
				f"Введите {self.entity_name.capitalize()} ID:", reply_markup=admin_cancel_keyboard()
			)
			await state.set_state(self.states.enter_show_id)
			await state.update_data(action="show")
			await callback.answer()

		@self.router.message(self.states.enter_show_id, F.text.regexp(r"^\d+$"))
		async def show_by_id(message: Message, state: FSMContext):
			log.debug(f"Вывод профиля {self.entity_name.capitalize()}. Проверка ID и наличия записи в БД")

			data = await state.get_data()
			action = data.get("action")
			log.debug(f"Действие: {action}")

			if action != "show":
				log.debug(f"Неверное действие: {action}")
				return

			try:
				item_id = int(message.text)
			except ValueError:
				await message.answer(
					f"Некорректный {self.entity_name.capitalize()} ID. Введите ID:",
					reply_markup=self.back_keyboard,
				)
				return

			item = await self.repo.get_by_id(item_id)
			if not item:
				await message.answer(
					f"{self.entity_name.capitalize()} не найден",
					reply_markup=self.back_keyboard,
				)
				await state.clear()
				return

			await state.update_data(current_id=item_id)
			await self._show_profile(message, item)

	# === Добавление ===
	def _register_add(self):
		@self.router.callback_query(F.data == f"{self.entity_name}_add")
		async def add_start(callback: CallbackQuery, state: FSMContext):
			log.debug(f"Добавление {self.entity_name}. Начало")

			await state.clear()
			await state.update_data(fields={}, step=0, action="add")
			field = self.add_fields[0]
			await callback.message.edit_text(
	            self.field_prompts[field], reply_markup=admin_cancel_keyboard()
	        )
			await state.set_state(self.states.enter_add_field)
			await callback.answer()

		@self.router.message(self.states.enter_add_field)
		async def add_field(message: Message, state: FSMContext):
			log.debug(f"Добавление {self.entity_name}. Продолжение")

			data = await state.get_data()
			if data.get("action") != "add":
				return

			step = data["step"]
			field = self.add_fields[step]
			value = message.text.strip()

			validator = self.field_validators.get(field, lambda x: (True, None))
			valid, error = validator(value)
			if not valid:
				await message.answer(
	                error or "Неверное значение", reply_markup=admin_cancel_keyboard()
	            )
				return

			resolved_value = await self.resolve_field_value(field, value)
			fields = data.get("fields", {})
			fields[field] = resolved_value

			step += 1
			if step >= len(self.add_fields):
				# Создаём DTO и сохраняем
				try:
					dto = self.add_dto_class(**fields)
					result_id = await self.repo.add(dto)
					if result_id:
						log.debug(f"Запись {result_id} успешно добавлена в БД")
						await message.answer(
	                        "Успешно добавлено!", reply_markup=self.back_keyboard
	                    )
					else:
						log.debug(f"Ошибка при добавлении записи {result_id} в БД")
						await message.answer(
	                        "Ошибка при добавлении", reply_markup=self.back_keyboard
	                    )
				except Exception as e:
					log.debug(f"Ошибка: {e}")
					await message.answer(
	                    f"Ошибка: {e}", reply_markup=self.back_keyboard
	                )
				await state.clear()
			else:
				await state.update_data(fields=fields, step=step)
				next_field = self.add_fields[step]
				await message.answer(
					self.field_prompts[next_field], reply_markup=admin_cancel_keyboard()
				)

	# === Удаление ===
	def _register_delete(self):
		@self.router.callback_query(F.data == f"{self.entity_name}_delete")
		async def delete_start(callback: CallbackQuery, state: FSMContext):
			log.debug(f"Удаление {self.entity_name}. Запрос подтверждения")
			data = await state.get_data()
			item_id = data.get("current_id")
			if not item_id:
				await callback.answer("Сначала выберите элемент", show_alert=True)
				return

			item = await self.repo.get_by_id(item_id)
			name = getattr(item, "name", getattr(item, "id", item_id))
			await callback.message.edit_text(
	            f"Удалить {self.entity_name} `{name}`?",
	            reply_markup=admin_confirmation_keyboard(),
	            parse_mode="Markdown",
	        )
			await state.set_state(self.states.confirm_delete)
			await callback.answer()

		@self.router.callback_query(self.states.confirm_delete, F.data == "admin_ok")
		async def delete_confirm(callback: CallbackQuery, state: FSMContext):
			data = await state.get_data()
			item_id = data.get("current_id")
			success = await self.repo.delete(item_id)
			await callback.message.edit_text(
	            "Удалено!" if success else "Ошибка удаления",
	            reply_markup=self.back_keyboard,
	        )
			await state.clear()
			await callback.answer()
