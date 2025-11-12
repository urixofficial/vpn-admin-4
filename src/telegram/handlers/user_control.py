from datetime import date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.core.logger import log
from src.core.dto import UserAddDTO, UserDTO, UserStatus
from src.db.repositories import user_repo, registration_repo
from src.telegram.interface import USER_LIST_HEADER, USER_LIST_ROW, USER_LIST_STATUS_ACTIVE, USER_LIST_STATUS_INACTIVE, \
	ENTER_USER_ID, USER_ID_NOT_NUMBER, USER_EXISTS, USER_NOT_FOUND, USER_PROFILE_TEMPLATE, ENTER_NAME, NAME_EMPTY, \
	NAME_TOO_LONG, USER_ADDED_SUCCESS, USER_ADDED_ERROR, USER_DELETE_CONFIRM, USER_DELETED_SUCCESS, USER_DELETED_ERROR, \
	FEATURE_IN_DEV, SEP, EDIT_BUTTON, DELETE_BUTTON, BACK_BUTTON, REG_SUCCESS_USER, REG_SUCCESS_ADMIN, \
	REG_REJECTED_USER, REG_REJECTED_ADMIN, USER_LIST_EMPTY

from src.telegram.keyboards import (admin_cancel_keyboard, admin_confirmation_keyboard,
                                    to_user_control_keyboard, user_profile_keyboard)


router = Router(name="user_control_handler")

class UserControlStates(StatesGroup):
	enter_user_id = State()
	enter_user_name = State()
	confirm_user_delete = State()
	confirm_registration = State()


# Вывод списка пользователей
@router.callback_query(F.data == "user_list")
async def cb_user_list(callback: CallbackQuery):
	log.debug("Вывод списка пользователей")

	users = await user_repo.get_all()
	if not users:
		await callback.answer()
		await callback.message.edit_text(USER_LIST_EMPTY, reply_markup=to_user_control_keyboard())
		return

	msg = USER_LIST_HEADER
	for user in users:
		status = USER_LIST_STATUS_ACTIVE if user.status == UserStatus.ACTIVE else USER_LIST_STATUS_INACTIVE
		msg += USER_LIST_ROW.format(
			status=status,
			name=user.name,
			user_id=user.id
		)

	await callback.answer()
	await callback.message.edit_text(msg, reply_markup=to_user_control_keyboard())


# Вывод профиля пользователя
async def show_user_info(message: Message, state: FSMContext, user: UserDTO):
	log.debug(f"Вывод профиля пользователя {user.name} ({user.id})")

	user_profile = USER_PROFILE_TEMPLATE.format(
		user_id=user.id,
		name=user.name,
		status=user.status.value,
		start_date=user.billing_start_date,
		end_date=user.billing_end_date,
		sep=SEP
	)

	await message.answer(user_profile, reply_markup=user_profile_keyboard())
	await state.update_data(user_id=user.id) # для передачи ID в хэндлеры CRUD-операций


# =====================================================================================================================
# ================================================ CRUD ===============================================================
# =====================================================================================================================

# Запрос ID пользователя
@router.callback_query(F.data.in_({"user_show", "user_add"}))
async def ask_user_id(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос ID пользователя")

	operation = callback.data.split("_")[1] # show or add
	await state.update_data(operation=operation)

	await callback.answer()
	await callback.message.edit_text(ENTER_USER_ID, reply_markup=to_user_control_keyboard())
	await state.set_state(UserControlStates.enter_user_id)


# Проверка ID и выбор следующего шага
@router.message(UserControlStates.enter_user_id)
async def check_user_id(message: Message, state: FSMContext):
	log.debug("Проверка ID пользователя")

	# Валидация ID
	try:
		user_id = int(message.text)
	except ValueError:
		await message.answer(USER_ID_NOT_NUMBER)
		return

	data = await state.get_data()
	operation = data["operation"]
	user = await user_repo.get_by_id(user_id)

	# Выбор следующего шага
	match operation:
		case "add":
			if user:
				await message.answer(USER_EXISTS, reply_markup=to_user_control_keyboard())
				await state.clear()
				return
			await state.update_data(user_id=user_id)
			await ask_name(message, state)
		case "show":
			if not user:
				await message.answer(USER_NOT_FOUND, reply_markup=to_user_control_keyboard())
				await state.clear()
				return
			await show_user_info(message, state, user)


# Запрос имени пользователя
async def ask_name(message: Message, state: FSMContext):
	log.debug("Запрос имени пользователя")

	# Отправка сообщения с запросом имени
	await message.answer(ENTER_NAME, reply_markup=admin_cancel_keyboard())
	await state.set_state(UserControlStates.enter_user_name)


# Проверка имени и добавление в базу
@router.message(UserControlStates.enter_user_name)
async def check_name(message: Message, state: FSMContext):
	log.debug("Проверка имени пользователя")

	# Валидация имени
	name = message.text.strip()
	if not name:
		await message.answer(NAME_EMPTY, reply_markup=admin_cancel_keyboard())
	if len(name) > 25:
		await message.answer(NAME_TOO_LONG, reply_markup=admin_cancel_keyboard())

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
		msg = USER_ADDED_SUCCESS.format(user_id=user_id, name=name)
	else:
		log.error(f"Ошибка при добавлении пользователя {user.name} в базу данных")
		msg = USER_ADDED_ERROR.format(user_id=user_id, name=name)
	await message.answer(msg, reply_markup=to_user_control_keyboard())


# Удаление пользователя. Запрос подтверждения
@router.callback_query(F.data == "user_delete")
async def ask_confirmation(callback: CallbackQuery, state: FSMContext):
	data = await state.get_data()
	user_id = data["user_id"]
	log.debug(f"Запрос подтверждения на удаление пользователя {user_id}")

	# Формирование запроса
	user = await user_repo.get_by_id(user_id)

	# Отправка сообщения с запросом подтверждения
	await callback.answer()
	await callback.message.edit_text(
		USER_DELETE_CONFIRM.format(user_id=user_id, name=user.name),
		reply_markup=admin_confirmation_keyboard()
	)
	await state.set_state(UserControlStates.confirm_user_delete)


# Удаление пользователя. Подтверждение получено
@router.callback_query(UserControlStates.confirm_user_delete, F.data == "admin_ok")
async def confirmation_approved(callback: CallbackQuery, state: FSMContext):
	log.debug("Подтверждение удаления пользователя получено")

	# Чтение операции
	data = await state.get_data()
	user_id = data["user_id"]
	user = await user_repo.get_by_id(user_id)

	success = await user_repo.delete(user_id)
	if success:
		log.info(f"Пользователь {user.name} успешно удален из базы данных")
		msg = USER_DELETED_SUCCESS
	else:
		log.error(f"Ошибка при удалении пользователя {user.name} из базы данных")
		msg = USER_DELETED_ERROR

	await callback.answer()
	await callback.message.edit_text(msg, reply_markup=to_user_control_keyboard())
	await state.clear()


# Редактирование пользователя
@router.callback_query(F.data == "user_edit")
async def user_edit(callback: CallbackQuery, state: FSMContext):
	data = await state.get_data()
	user_id = data["user_id"]
	log.debug(f"Редактирование пользователя {user_id}")

	await callback.answer(FEATURE_IN_DEV)


# =====================================================================================================================
# ============================================= Блокировка ============================================================
# =====================================================================================================================

# Блокировка пользователя
@router.callback_query(F.data == "user_block")
async def user_block(callback: CallbackQuery, state: FSMContext):
	log.debug("Блокировка пользователя")

	await callback.answer(FEATURE_IN_DEV)


# Разблокировка пользователя
@router.callback_query(F.data == "user_unblock")
async def user_unblock(callback: CallbackQuery, state: FSMContext):
	log.debug("Разблокировка пользователя")

	await callback.answer(FEATURE_IN_DEV)


# =====================================================================================================================
# ============================================= Регистрация ===========================================================
# =====================================================================================================================

# Регистрация подтверждена. Внесение пользователя в базу
@router.callback_query(F.data.startswith("registration_approve_"))
async def approve_registration(callback: CallbackQuery):
	user_id = int(callback.data.split("_")[-1])
	log.debug(f"Админ одобрил регистрацию пользователя {user_id}")

	registration_dto = await registration_repo.get_by_id(user_id)
	if not registration_dto:
		log.error(f"Ошибка: не найдена запись c ID={user_id} в таблице регистрации")
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
		user_msg = REG_SUCCESS_USER
		admin_msg = REG_SUCCESS_ADMIN
		log.info(f"Пользователь {user.name} ({user.id}) успешно зарегистрирован.")
	else:
		user_msg = REG_REJECTED_USER
		admin_msg = REG_REJECTED_ADMIN
		log.error(f"Ошибка при добавлении пользователя {user.name} ({user.id})")

	await registration_repo.delete(user_id)
	await callback.answer()
	await callback.message.edit_text(admin_msg, reply_markup=None)
	await callback.bot.send_message(chat_id=user_id, text=user_msg)


# Регистрация отклонена
@router.callback_query(F.data.startswith("registration_reject_"))
async def reject_registration(callback: CallbackQuery):
	user_id = int(callback.data.split("_")[-1])
	log.debug(f"Админ отклонил регистрацию пользователя {user_id}")

	await callback.answer()
	await callback.bot.send_message(chat_id=user_id, text=REG_REJECTED_USER)
	await callback.message.edit_text(REG_REJECTED_ADMIN.format(user_id=user_id), reply_markup=None)

