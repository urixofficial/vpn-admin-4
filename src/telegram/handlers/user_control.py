from datetime import date

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
	Message, InlineKeyboardMarkup, InlineKeyboardButton,
	CallbackQuery
)

from src.core.config import settings
from src.core.logger import log
from src.core.dto import UserDTO, UserStatus
from src.db.repositories import user_repo

from src.telegram.keyboards import (cancel_keyboard, admin_panel_keyboard, user_control_keyboard,
                                    confirmation_keyboard, to_user_control_keyboard)


router = Router(name="user_control_handler")

class CrudStates(StatesGroup):
	enter_id = State()
	enter_name = State()
	enter_date = State()
	confirm = State()

# === Вывод списка пользователей ===

@router.callback_query(F.data == "user_list")
async def cb_list_users(callback: CallbackQuery):
	users = await user_repo.get_all()
	if not users:
		await callback.answer()
		await callback.message.edit_text("Нет пользователей.", reply_markup=to_user_control_keyboard())
		return

	text = "Список пользователей:\n\n"
	for user in users:
		status = "✅" if user.status == UserStatus.ACTIVE else "❌"
		text += f"{status} {user.name} ({user.id})\n"

	await callback.answer()
	await callback.message.edit_text(text, parse_mode="HTML", reply_markup=to_user_control_keyboard())

# === CRUD-операции ===

# Запрос ID
@router.callback_query(F.data.in_({"user_add", "user_update", "user_delete"}))
async def ask_user_id(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос ID пользователя")
	operation = callback.data.split("_")[1] # add / update / delete
	await state.update_data(operation=operation)
	await callback.message.edit_text("Введите ID пользователя:", reply_markup=cancel_keyboard())
	await state.set_state(CrudStates.enter_id)

# Проверка ID и выбор следующего шага
@router.message(CrudStates.enter_id)
async def check_user_id(message: Message, state: FSMContext):
	log.debug("Проверка ID пользователя")

	# Валидация ID
	try:
		user_id = int(message.text)
	except ValueError:
		await message.answer("ID должен быть числом. Введите ID пользователя:")
		return

	user = await user_repo.get_by_id(user_id)

	# Сохранение ID в буфер и чтение типа операции
	await state.update_data(user_id=user_id)
	data = await state.get_data()
	operation = data["operation"]

	# Выбор следующего действия
	if operation == "add":
		if user:
			await message.answer(f"Пользователь с ID={user_id} уже существует")
			await state.clear()
			return
		await ask_name(message, state)
	elif operation == "update":
		pass
	elif operation == "delete":
		if not user:
			await message.answer(f"Пользователь с ID={user_id} не найден")
			await state.clear()
			return
		await ask_confirmation(message, state)
	else:
		log.debug("Операция не определена")
		await message.answer("Внутренняя ошибка")
		await state.clear()
		return

# Запрос имени
async def ask_name(message: Message, state: FSMContext):
	log.debug("Запрос имени пользователя")

	# Отправка сообщения с запросом имени
	await message.answer("Введите имя пользователя", reply_markup=cancel_keyboard())
	await state.set_state(CrudStates.enter_name)

# Проверка имени и выбор следующего шага
@router.message(CrudStates.enter_name)
async def check_name(message: Message, state: FSMContext):
	log.debug("Проверка имени пользователя")

	# Валидация имени
	name = message.text.strip()
	if not name:
		await message.answer("Имя не может быть пустым. Введите имя пользователя:",
		                     reply_markup=cancel_keyboard())

	# Сохранение ID в буфер и чтение типа операции
	await state.update_data(name=name)
	data = await state.get_data()
	operation = data["operation"]

	# Выбор следующего шага
	if operation == "add":
		await ask_confirmation(message, state)


# Запрос подтверждения
async def ask_confirmation(message: Message, state: FSMContext):
	log.debug("Запрос подтверждения")

	# Чтение операции
	data = await state.get_data()
	operation = data["operation"]

	# Составление сообщения для подтверждения
	if operation == "add":
		msg = (f"Добавить пользователя?\n\n"
		       f"ID: {data["user_id"]}\n"
		       f"Имя: {data["name"]}")
	elif operation == "update":
		msg = "Обновить данные пользователя?"
	elif operation == "delete":
		user_dto = await user_repo.get_by_id(data["user_id"])
		msg = ("Удалить пользователя?\n\n"
		       f"ID: {data["user_id"]}\n"
		       f"Имя: {user_dto.name}")
	else:
		return

	# Отправка сообщения с запросом подтверждения
	await message.answer(msg, reply_markup=confirmation_keyboard())
	await state.set_state(CrudStates.confirm)

# Подтверждение получено
@router.callback_query(CrudStates.confirm, F.data == "ok")
async def confirmation_approved(callback: CallbackQuery, state: FSMContext):
	log.debug("Подтверждение получено")

	# Чтение операции
	data = await state.get_data()
	operation = data["operation"]

	# Составление сообщения для подтверждения
	if operation == "add":
		await callback.answer()
		success = await add_user_to_db(state)
		msg = "✅ Пользователь успешно добавлен!" if success else "❌ Ошибка добавления пользователя"
		await callback.message.edit_text(msg, reply_markup=to_user_control_keyboard())
		await state.clear()
	elif operation == "update":
		pass
	elif operation == "delete":
		await callback.answer()
		success = await delete_user_from_db(state)
		msg = "✅ Пользователь успешно удален!" if success else "❌ Ошибка удаления пользователя"
		await callback.message.edit_text(msg, reply_markup=to_user_control_keyboard())
		await state.clear()
	else:
		return

# Подтверждение отклонено
@router.callback_query(CrudStates.confirm, F.data == "cancel")
async def confirmation_canceled(callback: CallbackQuery, state: FSMContext):
	log.debug("Подтверждение отклонено")

	await callback.answer()
	await callback.message.edit_text("Действие отменено", reply_markup=to_user_control_keyboard())
	await state.clear()

# Добавление пользователя в базу данных
async def add_user_to_db(state: FSMContext):
	log.debug("Добавление пользователя в базу данных")

	# Чтение данных
	data = await state.get_data()
	user_id = data["user_id"]
	name = data["name"]

	# Создание модели DTO
	user_dto = UserDTO(
		id = user_id,
		name=name,
		billing_start_date=date.today(),
		billing_end_date=date.today(),
		blocked=False
	)

	# Добавление в базу данных
	success = await user_repo.add(user_dto)
	return success

# Добавление пользователя в базу данных
async def delete_user_from_db(state: FSMContext):
	log.debug("Удаление пользователя из базы данных")

	# Чтение данных
	data = await state.get_data()
	user_id = data["user_id"]

	# Добавление в базу данных
	success = await user_repo.delete(user_id)
	return success