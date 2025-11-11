# src/telegram/handlers/user.py

from datetime import date

from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from src.core.logger import log
from src.core.config import settings
from src.db.repositories import user_repo, registration_repo
from src.telegram.keyboards import (user_register_keyboard, admin_confirmation_keyboard, user_confirmation_keyboard,
                                    user_cancel_keyboard)
from src.core.dto import RegistrationAddDTO
from src.telegram.interface import USER_PROFILE_TEMPLATE, SEP, USER_NOT_REGISTERED, ACTION_CANCELED, ENTER_NAME, \
	NAME_EMPTY, NAME_NOT_UNIQUE, REG_USER_CONFIRM, REG_ADMIN_CONFIRM, REG_REQUEST_SENT, REG_ERROR_USER

router = Router(name="user_handler")


class RegisterStates(StatesGroup):
	waiting_name = State()
	waiting_confirm = State()


# Обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
	user_id = message.from_user.id
	log.info(f"Пользователь {user_id} выполнил команду /start")

	await welcome_message(message)


# Вывод приветственного сообщения
async def welcome_message(message: Message):
	log.debug(f"Вывод приветственного сообщения пользователю {message.from_user.id}")


	user = await user_repo.get_by_id(message.from_user.id)


	if user:
		user_profile = USER_PROFILE_TEMPLATE.format(
			user_id=user.id,
			name=user.name,
			status=user.status.value,
			start_date=user.billing_start_date,
			end_date=user.billing_end_date,
			sep=SEP
		)
		await message.answer(user_profile)
	else:
		await message.answer(
			USER_NOT_REGISTERED,
			reply_markup=user_register_keyboard()
		)


# Отмена текущего действия
@router.callback_query(F.data == "user_cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
	log.debug(f"Пользователь {callback.from_user.id} отменил действие")

	await callback.answer()
	await state.clear()
	await callback.message.edit_text(ACTION_CANCELED)


# Запрос имени
@router.callback_query(F.data == "register")
async def ask_name(callback: CallbackQuery, state: FSMContext):
	log.debug(f"Запрос имени у пользователя {callback.from_user.id}")

	await callback.answer()
	await callback.message.edit_text(ENTER_NAME, reply_markup=user_cancel_keyboard())
	await state.set_state(RegisterStates.waiting_name)


# Проверка имени
@router.message(RegisterStates.waiting_name)
async def check_name(message: Message, state: FSMContext):
	log.debug(f"Проверка ввода имени пользователя {message.from_user.id}")

	name = message.text.strip()

	# Проверка наличия имени
	if not name:
		await message.answer(NAME_EMPTY)
		return

	# Проверка уникальности имени
	all_users = await user_repo.get_all()
	if all_users and any(u.name.lower() == name.lower() for u in all_users):
		await message.answer(NAME_NOT_UNIQUE)
		return

	# Сохранение имени в буфер
	await state.update_data(name=name)
	msg = REG_USER_CONFIRM

	# Отправка запроса на подтверждение
	await message.answer(msg, reply_markup=user_confirmation_keyboard())
	await state.set_state(RegisterStates.waiting_confirm)


# Отправка запроса администратору
@router.callback_query(RegisterStates.waiting_confirm, F.data == "user_ok")
async def cb_confirm_registration(callback: CallbackQuery, state: FSMContext):
	log.debug(f"Подтверждение регистрации пользователя {callback.from_user.id} получено. Отправка запроса администратору")

	# Чтение данных из буфера
	data = await state.get_data()
	name = data["name"]
	user_id = callback.from_user.id

	# Добавление записи в таблицу регистрации
	registration_dto = RegistrationAddDTO(
		id=user_id,
		name = name
	)
	await registration_repo.add(registration_dto)

	# Отправка сообщения админу
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Подтвердить", callback_data=f"registration_approve_{user_id}"),
				InlineKeyboardButton(text="Отклонить", callback_data=f"registration_reject_{user_id}"),
			]
		]
	)

	await callback.answer()
	try:
		await callback.bot.send_message(
			chat_id=settings.TELEGRAM_ADMIN_ID,
			text=REG_ADMIN_CONFIRM,
			reply_markup=keyboard
		)
		log.debug(f"Запрос на регистрацию от {name} ({user_id}) отправлен администратору")
		await callback.message.edit_text(REG_REQUEST_SENT)
	except Exception as e:
		log.error(f"Ошибка отправки админу: {e}")
		await callback.message.edit_text(REG_ERROR_USER)

	await state.clear()


# Обработка всех остальных сообщений
@router.message(F.text)
async def handle_any_text(message: Message):
	log.info(f"Пользователь {message.from_user.id} отправил сообщение: {message.text}")

	await welcome_message(message)