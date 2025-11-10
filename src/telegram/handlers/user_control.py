from datetime import date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from src.core.logger import log
from src.core.dto import UserDTO, UserStatus
from src.db.repositories import user_repo

from src.telegram.keyboards import (cancel_keyboard, confirmation_keyboard,
                                    to_user_control1_keyboard, user_profile_keyboard)


router = Router(name="user_control_handler")

class UserControlStates(StatesGroup):
	enter_id = State()
	enter_name = State()
	confirm = State()


# Вывод списка пользователей
@router.callback_query(F.data == "user_list")
async def cb_user_list(callback: CallbackQuery):
	log.debug("Вывод списка пользователей")

	users = await user_repo.get_all()
	if not users:
		await callback.answer()
		await callback.message.edit_text("Нет пользователей.", reply_markup=to_user_control1_keyboard())
		return

	text = "Список пользователей:\n\n"
	for user in users:
		status = "✅" if user.status == UserStatus.ACTIVE else "❌"
		text += f"{status} {user.name} ({user.id})\n"

	await callback.answer()
	await callback.message.edit_text(text, parse_mode="HTML", reply_markup=to_user_control1_keyboard())


# Запрос ID пользователя
@router.callback_query(F.data.in_({"user_choose", "user_add"}))
async def cb_user_choose(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос ID пользователя")

	operation = callback.data.split("_")[1] # choose or add
	await state.update_data(operation=operation)

	await callback.answer()
	await callback.message.edit_text("Введите ID пользователя:", reply_markup=to_user_control1_keyboard())
	await state.set_state(UserControlStates.enter_id)


# Проверка ID и выбор следующего шага
@router.message(UserControlStates.enter_id)
async def check_user_id(message: Message, state: FSMContext):
	log.debug("Проверка ID пользователя")

	# Валидация ID
	try:
		user_id = int(message.text)
	except ValueError:
		await message.answer("ID должен быть числом. Введите ID пользователя:")
		return

	data = await state.get_data()
	operation = data["operation"]
	user = await user_repo.get_by_id(user_id)

	# Выбор следующего шага
	match operation:
		case "add":
			if user:
				await message.answer(f"Пользователь с ID={user_id} уже существует")
				await state.clear()
				return
			await state.update_data(user_id=user_id)
			await ask_name(message, state)
		case "choose":
			await state.clear()
			if not user:
				await message.answer(f"Пользователь с ID={user_id} не найден")

				return
			await show_user_profile(message, state, user)


# Вывести профиль пользователя
async def show_user_profile(message: Message, state: FSMContext, user: UserDTO):
	log.debug(f"Вывод профиля пользователя {user.name} ({user.id})")

	info = (f"<b>{user.name}</b> ({user.id})\n"
	        f"{'-'*40}\n"
	        f"<code>Статус: | {user.status.value}</code>\n"
	        f"<code>Начало: | {user.billing_start_date}</code>\n"
	        f"<code>Конец:  | {user.billing_end_date}</code>\n")

	await message.answer(info, reply_markup=user_profile_keyboard(), parse_mode="HTML")
	await state.update_data(user_id=user.id)


# Запрос имени
async def ask_name(message: Message, state: FSMContext):
	log.debug("Запрос имени пользователя")

	# Отправка сообщения с запросом имени
	await message.answer("Введите имя пользователя", reply_markup=cancel_keyboard())
	await state.set_state(UserControlStates.enter_name)


# Проверка имени и выбор следующего шага
@router.message(UserControlStates.enter_name)
async def check_name(message: Message, state: FSMContext):
	log.debug("Проверка имени пользователя")

	# Валидация имени
	name = message.text.strip()
	if not name:
		await message.answer("Имя не может быть пустым. Введите имя пользователя:",
		                     reply_markup=cancel_keyboard())

	# Чтение данных
	data = await state.get_data()
	user_id = data["user_id"]

	# Создание модели DTO
	user = UserDTO(
		id=user_id,
		name=name,
		billing_start_date=date.today(),
		billing_end_date=date.today(),
		blocked=False
	)

	# Добавление в базу данных
	success = await user_repo.add(user)
	if success:
		log.info(f"Пользователь {user.name} успешно добавлен в базу данных")
		msg = (f"<b>{user.name}</b> ({user.id})\n"
		       f"{'-' * 40}\n"
		       f"✅ Пользователь успешно добавлен.")
	else:
		log.error(f"Ошибка при добавлении пользователя {user.name} в базу данных")
		msg = (f"<b>{user.name}</b> ({user.id})\n"
		       f"{'-' * 40}\n"
		       f"❌ Ошибка при добавлении пользователя.")
	await message.answer(msg, parse_mode="HTML", reply_markup=to_user_control1_keyboard())


# Запрос подтверждения на удаление
@router.callback_query(F.data == "user_delete")
async def ask_confirmation(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос подтверждения")

	# Формирование запроса
	data = await state.get_data()
	user_id = data["user_id"]
	user = await user_repo.get_by_id(user_id)

	# Отправка сообщения с запросом подтверждения
	await callback.answer()
	await callback.message.edit_text(f"Удалить пользователя {user.name}?", reply_markup=confirmation_keyboard())
	await state.set_state(UserControlStates.confirm)


# Подтверждение получено
@router.callback_query(UserControlStates.confirm, F.data == "ok")
async def confirmation_approved(callback: CallbackQuery, state: FSMContext):
	log.debug("Подтверждение получено")

	# Чтение операции
	data = await state.get_data()
	user_id = data["user_id"]
	user = await user_repo.get_by_id(user_id)

	success = await user_repo.delete(user_id)
	if success:
		log.info(f"Пользователь {user.name} успешно удален из базы данных")
		msg = (f"<b>{user.name}</b> ({user.id})\n"
		       f"{'-' * 40}\n"
		       f"✅ Пользователь успешно удален.")
	else:
		log.error(f"Ошибка при удалении пользователя {user.name} из базы данных")
		msg = (f"<b>{user.name}</b> ({user.id})\n"
		       f"{'-' * 40}\n"
		       f"❌ Ошибка при удалении пользователя.")

	await callback.answer()
	await callback.message.edit_text(msg, reply_markup=to_user_control1_keyboard(), parse_mode="HTML")
	await state.clear()


# Редактирование пользователя
@router.callback_query(F.data == "user_edit")
async def user_edit(callback: CallbackQuery, state: FSMContext):
	log.debug("Панель редактирования пользователя")

	await callback.answer("Функция в разработке")


# Блокировка пользователя
@router.callback_query(F.data == "user_block")
async def user_block(callback: CallbackQuery, state: FSMContext):
	log.debug("Блокировка пользователя")

	await callback.answer("Функция в разработке")


# Разблокировка пользователя
@router.callback_query(F.data == "user_unblock")
async def user_unblock(callback: CallbackQuery, state: FSMContext):
	log.debug("Разблокировка пользователя")

	await callback.answer("Функция в разработке")