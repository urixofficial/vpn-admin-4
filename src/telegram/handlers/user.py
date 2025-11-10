# src/telegram/handlers/user.py

from datetime import date

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from src.core.logger import log
from src.db.repositories import user_repo
from src.telegram.keyboards import register_keyboard

router = Router(name="user_handler")


class RegisterStates(StatesGroup):
	waiting_name = State()
	waiting_confirm = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
	user_id = message.from_user.id
	log.info(f"Пользователь с ID={user_id} выполнил команду /start")

	user = await user_repo.get_by_id(user_id)

	if user:
		msg = (
			f"Привет, {user.name}!\n"
			f"Ваш статус: {user.status.value}\n"
			f"Оплачено до: {user.billing_end_date}"
		)
		await message.answer(msg, parse_mode="HTML")
	else:
		await message.answer(
			"Вы не зарегистрированы. Обратитесь к @urixofficial для регистрации.",
			# reply_markup=register_keyboard()
		)


# @router.callback_query(F.data == "register")
# async def cb_register(callback: CallbackQuery, state: FSMContext):
# 	await callback.message.edit_text(
# 		"Введите ваше имя или псевдоним.\n"
# 		"<b>Важно:</b> имя должно быть уникальным.",
# 		parse_mode="HTML"
# 	)
# 	await state.set_state(RegisterStates.waiting_name)

#
# @router.message(RegisterStates.waiting_name)
# async def process_name(message: Message, state: FSMContext):
# 	name = message.text.strip()
#
# 	# Проверка наличия имени
# 	if not name:
# 		await message.answer("Имя не может быть пустым. Попробуйте ещё раз:")
# 		return
#
# 	# Проверка уникальности имени
# 	all_users = await user_repo.get_all()
# 	if all_users and any(u.name.lower() == name.lower() for u in all_users):
# 		await message.answer("Это имя уже занято. Выберите другое:")
# 		return
#
# 	# Сохраняем имя и ID
# 	await state.update_data(name=name, user_id_input=message.from_user.id)
#
# 	kb = InlineKeyboardMarkup(inline_keyboard=[
# 		[InlineKeyboardButton(text="ОК", callback_data="registration_ok")],
# 		[InlineKeyboardButton(text="Отмена", callback_data="registration_cancel")]
# 	])
# 	await message.answer(
# 		f"ID: <b>{message.from_user.id}</b>\n"
# 		f"Имя: <b>{name}</b>\n\n"
# 		f"Отправить запрос администратору?",
# 		reply_markup=kb,
# 		parse_mode="HTML"
# 	)
# 	await state.set_state(RegisterStates.waiting_confirm)
#
#
# @router.callback_query(F.data == "registration_ok")
# async def cb_confirm_registration(callback: CallbackQuery, state: FSMContext):
# 	data = await state.get_data()
# 	name = data["name"]
# 	user_id_input = data["user_id_input"]
#
# 	# Отправляем админу
# 	admin_kb = InlineKeyboardMarkup(inline_keyboard=[
# 		[InlineKeyboardButton(text="Подтвердить", callback_data=f"approve_reg_{user_id_input}_{name}")],
# 		[InlineKeyboardButton(text="Отклонить", callback_data=f"reject_reg_{user_id_input}")]
# 	])
# 	admin_text = (
# 		f"Запрос на регистрацию:\n\n"
# 		f"ID: <code>{user_id_input}</code>\n"
# 		f"Имя: <b>{name}</b>\n"
# 		f"Дата: {date.today()}"
# 	)
# 	try:
# 		await callback.bot.send_message(
# 			chat_id=settings.TELEGRAM_ADMIN_ID,
# 			text=admin_text,
# 			reply_markup=admin_kb,
# 			parse_mode="HTML"
# 		)
# 		await callback.message.edit_text("Запрос отправлен администратору. Ожидайте.")
# 	except Exception as e:
# 		await callback.message.edit_text("Ошибка отправки. Попробуйте позже.")
# 		log.error(f"Ошибка отправки админу: {e}")
#
# 	await state.clear()
#
#
# @router.callback_query(F.data == "registration_cancel")
# async def cb_cancel_registration(callback: CallbackQuery, state: FSMContext):
# 	await callback.message.edit_text("Регистрация отменена.")
# 	await state.clear()
