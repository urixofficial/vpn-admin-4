from datetime import date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from src.core.logger import log
from src.core.dto import UserAddDTO, UserDTO, UserStatus
from src.db.repositories import user_repo, registration_repo

from src.telegram.keyboards import (admin_cancel_keyboard, admin_confirmation_keyboard,
                                    to_user_control_keyboard, user_profile_keyboard, to_user_panel_keyboard)


router = Router(name="user_control_handler")

class UserControlStates(StatesGroup):
	enter_id = State()
	enter_name = State()
	confirm = State()
	registration_confirm = State()


# Вывод списка пользователей
@router.callback_query(F.data == "user_list")
async def cb_user_list(callback: CallbackQuery):
	log.debug("Вывод списка пользователей")

	users = await user_repo.get_all()
	if not users:
		await callback.answer()
		await callback.message.edit_text("Нет пользователей.", reply_markup=to_user_control_keyboard())
		return

	msg = "Список пользователей:\n\n"
	for user in users:
		status = "✅" if user.status == UserStatus.ACTIVE else "❌"
		msg += f"{status} {user.name} ({user.id})\n"

	await callback.answer()
	await callback.message.edit_text(msg, reply_markup=to_user_control_keyboard())


# Запрос ID пользователя
@router.callback_query(F.data.in_({"user_choose", "user_add"}))
async def cb_user_choose(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос ID пользователя")

	operation = callback.data.split("_")[1] # choose or add
	await state.update_data(operation=operation)

	await callback.answer()
	await callback.message.edit_text("Введите ID пользователя:", reply_markup=to_user_control_keyboard())
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
				await message.answer(f"Пользователь с ID={user_id} уже существует", reply_markup=to_user_control_keyboard())
				await state.clear()
				return
			await state.update_data(user_id=user_id)
			await ask_name(message, state)
		case "choose":
			if not user:
				await message.answer(f"Пользователь с ID={user_id} не найден", reply_markup=to_user_control_keyboard())
				await state.clear()
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

	await message.answer(info, reply_markup=user_profile_keyboard())
	await state.update_data(user_id=user.id)


# Запрос имени
async def ask_name(message: Message, state: FSMContext):
	log.debug("Запрос имени пользователя")

	# Отправка сообщения с запросом имени
	await message.answer("Введите имя пользователя", reply_markup=admin_cancel_keyboard())
	await state.set_state(UserControlStates.enter_name)


# Проверка имени и выбор следующего шага
@router.message(UserControlStates.enter_name)
async def check_name(message: Message, state: FSMContext):
	log.debug("Проверка имени пользователя")

	# Валидация имени
	name = message.text.strip()
	if not name:
		await message.answer("Имя не может быть пустым. Введите имя пользователя:",
		                     reply_markup=admin_cancel_keyboard())
	if len(name) > 25:
		await message.answer("Имя должно быть не длиннее 25 символов. Введите имя пользователя:",
		                     reply_markup=admin_cancel_keyboard())

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
	await message.answer(msg, reply_markup=to_user_control_keyboard())


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
	await callback.message.edit_text(f"Удалить пользователя {user.name}?", reply_markup=admin_confirmation_keyboard())
	await state.set_state(UserControlStates.confirm)


# Подтверждение получено
@router.callback_query(UserControlStates.confirm, F.data == "admin_ok")
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
	await callback.message.edit_text(msg, reply_markup=to_user_control_keyboard())
	await state.clear()


# Регистрация подтверждена. Внесение пользователя в базу
@router.callback_query(F.data.startswith("registration_approve_"))
async def approve_registration(callback: CallbackQuery):
	user_id = int(callback.data.split("_")[-1])
	log.debug(f"Админ одобрил регистрацию пользователя {user_id}")

	registration_dto = await registration_repo.get_by_id(user_id)
	if not registration_dto:
		log.error(f"Ошибка: не найдена запись c ID={user_id} в таблице ожидания регистрации")
		return

	user = UserAddDTO(
		id=user_id,
		name=registration_dto.name,
		billing_start_date=date.today(),
		billing_end_date=date.today(),
		blocked=False
	)

	success = await user_repo.add(user)

	if success:
		user_msg = "✅ Подтверждение получено. Вы успешно зарегистрированы!"
		admin_msg = "✅ Пользователь успешно добавлен."
		log.info(f"Пользователь {user.name} ({user.id}) успешно зарегистрирован.")
	else:
		user_msg = "❌ Подтверждение получено, но возникла ошибка при регистрации."
		admin_msg = "❌ Ошибка добавления пользователя в базу."
		log.error(f"Ошибка при добавлении пользователя {user.name} ({user.id})")

	await registration_repo.delete(user_id)
	await callback.answer("Одобрено")
	await callback.message.edit_text(admin_msg, reply_markup=None)
	await callback.bot.send_message(chat_id=user_id, text=user_msg)


# Регистрация отклонена
@router.callback_query(F.data.startswith("registration_reject_"))
async def reject_registration(callback: CallbackQuery):
	user_id = int(callback.data.split("_")[-1])
	log.debug(f"Админ отклонил регистрацию пользователя {user_id}")

	msg = "❌ Администратор отклонил ваш запрос."

	await callback.answer("Отклонено")
	await callback.bot.send_message(chat_id=user_id, text=msg)
	await callback.message.edit_text(f"❌ Регистрация пользователя {user_id} отклонена.", reply_markup=None)


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