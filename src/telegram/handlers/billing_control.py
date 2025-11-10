from datetime import date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from src.core.logger import log
from src.core.dto import UserDTO, UserStatus
from src.db.repositories import user_repo, billing_repo

from src.telegram.keyboards import (cancel_keyboard, confirmation_keyboard,
                                    to_billing_control_keyboard, user_profile_keyboard)


router = Router(name="billing_control_handler")

class BillingControlStates(StatesGroup):
	enter_user_id = State()
	enter_amount = State()
	confirm = State()


# Вывод списка транзакций
@router.callback_query(F.data == "tx_list")
async def cb_user_list(callback: CallbackQuery):
	log.debug("Вывод списка транзакций")

	transactions = await billing_repo.get_all()
	if not transactions:
		await callback.answer()
		await callback.message.edit_text("Нет транзакций.", reply_markup=to_billing_control_keyboard())
		return

	msg = "Список транзакций:\n\n"
	for transaction in transactions:
		msg += f"<code>{transaction.id} | {transaction.amount} | {transaction.user_id}\n</code>"

	await callback.answer()
	await callback.message.edit_text(msg, parse_mode="HTML", reply_markup=to_billing_control_keyboard())


# Запрос ID пользователя
# @router.callback_query(F.data.in_({"user_choose", "user_add"}))
# async def cb_user_choose(callback: CallbackQuery, state: FSMContext):
# 	log.debug("Запрос ID пользователя")
#
# 	operation = callback.data.split("_")[1] # choose or add
# 	await state.update_data(operation=operation)
#
# 	await callback.answer()
# 	await callback.message.edit_text("Введите ID пользователя:", reply_markup=to_user_control_keyboard())
# 	await state.set_state(UserControlStates.enter_id)


# Проверка ID и выбор следующего шага
# @router.message(UserControlStates.enter_id)
# async def check_user_id(message: Message, state: FSMContext):
# 	log.debug("Проверка ID пользователя")
#
# 	# Валидация ID
# 	try:
# 		user_id = int(message.text)
# 	except ValueError:
# 		await message.answer("ID должен быть числом. Введите ID пользователя:")
# 		return
#
# 	data = await state.get_data()
# 	operation = data["operation"]
# 	user = await user_repo.get_by_id(user_id)
#
# 	# Выбор следующего шага
# 	match operation:
# 		case "add":
# 			if user:
# 				await message.answer(f"Пользователь с ID={user_id} уже существует", reply_markup=to_user_control_keyboard())
# 				await state.clear()
# 				return
# 			await state.update_data(user_id=user_id)
# 			await ask_name(message, state)
# 		case "choose":
# 			if not user:
# 				await message.answer(f"Пользователь с ID={user_id} не найден", reply_markup=to_user_control_keyboard())
# 				await state.clear()
# 				return
# 			await show_user_profile(message, state, user)


# Вывести профиль пользователя
# async def show_user_profile(message: Message, state: FSMContext, user: UserDTO):
# 	log.debug(f"Вывод профиля пользователя {user.name} ({user.id})")
#
# 	info = (f"<b>{user.name}</b> ({user.id})\n"
# 	        f"{'-'*40}\n"
# 	        f"<code>Статус: | {user.status.value}</code>\n"
# 	        f"<code>Начало: | {user.billing_start_date}</code>\n"
# 	        f"<code>Конец:  | {user.billing_end_date}</code>\n")
#
# 	await message.answer(info, reply_markup=user_profile_keyboard(), parse_mode="HTML")
# 	await state.update_data(user_id=user.id)


# Запрос имени
# async def ask_name(message: Message, state: FSMContext):
# 	log.debug("Запрос имени пользователя")
#
# 	# Отправка сообщения с запросом имени
# 	await message.answer("Введите имя пользователя", reply_markup=cancel_keyboard())
# 	await state.set_state(UserControlStates.enter_name)


# Проверка имени и выбор следующего шага
# @router.message(UserControlStates.enter_name)
# async def check_name(message: Message, state: FSMContext):
# 	log.debug("Проверка имени пользователя")
#
# 	# Валидация имени
# 	name = message.text.strip()
# 	if not name:
# 		await message.answer("Имя не может быть пустым. Введите имя пользователя:",
# 		                     reply_markup=cancel_keyboard())
# 	if len(name) > 25:
# 		await message.answer("Имя должно быть не длиннее 25 символов. Введите имя пользователя:",
# 		                     reply_markup=cancel_keyboard())
#
# 	# Чтение данных
# 	data = await state.get_data()
# 	user_id = data["user_id"]
#
# 	# Создание модели DTO
# 	user = UserDTO(
# 		id=user_id,
# 		name=name,
# 		billing_start_date=date.today(),
# 		billing_end_date=date.today(),
# 		blocked=False
# 	)
#
# 	# Добавление в базу данных
# 	success = await user_repo.add(user)
# 	if success:
# 		log.info(f"Пользователь {user.name} успешно добавлен в базу данных")
# 		msg = (f"<b>{user.name}</b> ({user.id})\n"
# 		       f"{'-' * 40}\n"
# 		       f"✅ Пользователь успешно добавлен.")
# 	else:
# 		log.error(f"Ошибка при добавлении пользователя {user.name} в базу данных")
# 		msg = (f"<b>{user.name}</b> ({user.id})\n"
# 		       f"{'-' * 40}\n"
# 		       f"❌ Ошибка при добавлении пользователя.")
# 	await message.answer(msg, parse_mode="HTML", reply_markup=to_user_control_keyboard())