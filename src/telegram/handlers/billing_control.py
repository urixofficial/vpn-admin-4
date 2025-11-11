from datetime import datetime, date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from src.core.logger import log
from src.core.dto import UserDTO, UserStatus, TransactionAddDTO, TransactionDTO
from src.db.repositories import user_repo, billing_repo

from src.telegram.keyboards import (admin_cancel_keyboard, admin_confirmation_keyboard,
                                    to_billing_control_keyboard, user_profile_keyboard)


router = Router(name="billing_control_handler")

class BillingControlStates(StatesGroup):
	enter_user_id = State()
	enter_tx_id = State()
	enter_amount = State()
	confirm = State()


# Вывод списка транзакций
@router.callback_query(F.data == "tx_list")
async def cb_tx_list(callback: CallbackQuery):
	log.debug("Вывод списка транзакций")

	transactions = await billing_repo.get_all()
	if not transactions:
		await callback.answer()
		await callback.message.edit_text("Нет транзакций.", reply_markup=to_billing_control_keyboard())
		return

	msg = (f"Список транзакций:\n\n"
	       f"<code>{'-' * 35}\n</code>"
	       f"<code> id | Сумма | Пользователь\n</code>"
	       f"<code>{'-' * 35}\n</code>")
	for transaction in transactions:
		user = await user_repo.get_by_id(transaction.user_id)
		msg += f"<code>{transaction.id:03d} | {transaction.amount: 5d} | {user.name}\n</code>"

	await callback.answer()
	await callback.message.edit_text(msg, reply_markup=to_billing_control_keyboard())


# Запрос ID пользователя
@router.callback_query(F.data == "tx_add")
async def ask_user_id(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос ID пользователя")

	await callback.answer()
	await callback.message.edit_text("Введите ID пользователя:", reply_markup=to_billing_control_keyboard())
	await state.set_state(BillingControlStates.enter_user_id)


# Проверка ID пользователя
@router.message(BillingControlStates.enter_user_id)
async def check_user_id(message: Message, state: FSMContext):
	log.debug("Проверка ID пользователя")

	# Валидация ID
	try:
		user_id = int(message.text)
	except ValueError:
		await message.answer("ID должен быть числом. Введите ID пользователя:")
		return

	# Проверка наличия пользователя в базе данных
	user = await user_repo.get_by_id(user_id)
	if not user:
		await message.answer(f"Пользователь с ID={user_id} не найден", reply_markup=to_billing_control_keyboard())
		await state.clear()
		return

	# Переход к следующему шагу
	await state.update_data(user_id=user_id)
	await ask_amount(message, state)


# Запрос суммы транзакции
async def ask_amount(message: Message, state: FSMContext):
	log.debug("Запрос суммы транзакции")

	await message.answer("Введите сумму транзакции", reply_markup=admin_cancel_keyboard())
	await state.set_state(BillingControlStates.enter_amount)


# Проверка суммы транзакции и добавление в БД
@router.message(BillingControlStates.enter_amount)
async def check_amount_save_to_db(message: Message, state: FSMContext):
	log.debug("Проверка суммы транзакции")

	# Валидация суммы
	try:
		amount = int(message.text)
	except ValueError:
		await message.answer("Сумма должна быть целым числом.\nВведите сумму транзакции:",
		                     reply_markup=admin_cancel_keyboard())
		return

	if amount <= 0 or amount % 100 != 0:
		await message.answer("Сумма должна быть больше нуля и кратна 100 рублям.\nВведите сумму транзакции:",
		                     reply_markup=admin_cancel_keyboard())
		return

	# Чтение данных из буфера
	data = await state.get_data()
	user_id = data["user_id"]
	user = await user_repo.get_by_id(user_id)

	# Создание модели DTO
	transaction = TransactionAddDTO(
		user_id=user_id,
		amount=amount,
		created_at=datetime.now(),
		updated_at=datetime.now()
	)

	# Добавление в базу данных
	transaction_id = await billing_repo.add(transaction)
	if transaction_id is not None:
		log.info(f"Транзакция успешно добавлена в базу данных")
		msg = (
			f"<code>"
			f" id | Сумма | Пользователь\n"
			f"{'-' * 35}\n"
			f"{transaction_id:03d} | {transaction.amount: 5d} | {user.name}\n"
			f"{'-' * 35}\n"
			f"✅ Транзакция успешно добавлена."
			f"</code>"
		)
	else:
		log.error(f"Ошибка при добавлении транзакции в базу данных")
		msg = (
			f"<code>"
			f" id | Сумма | Пользователь\n"
			f"{'-' * 35}\n"
			f"{transaction_id:03d} | {transaction.amount: 5d} | {user.name}\n"
			f"{'-' * 35}\n"
			f"❌ Ошибка при добавлении транзакции."
			f"</code>"
		)

	await message.answer(msg, reply_markup=to_billing_control_keyboard())


# Изменение транзакции
@router.callback_query(F.data == "tx_edit")
async def tx_edit(callback: CallbackQuery, state: FSMContext):
	log.debug("Обновление транзакции")

	await callback.answer("Функция в разработке")


# Удаление транзакции
@router.callback_query(F.data == "tx_delete")
async def tx_delete_ask_tx_id(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос ID транзакции")

	await callback.answer()
	await callback.message.edit_text("Введите ID транзакции:", reply_markup=admin_cancel_keyboard())
	await state.set_state(BillingControlStates.enter_tx_id)


# Проверка ID транзакции и переход к следующему шагу
@router.message(BillingControlStates.enter_tx_id)
async def check_tx_id(message: Message, state: FSMContext):
	log.debug("Проверка ID транзакции")

	# Валидация ID
	try:
		transaction_id = int(message.text)
	except ValueError:
		await message.answer("ID должен быть целым числом. Введите ID транзакции:", reply_markup=admin_cancel_keyboard())
		return

	if transaction_id <= 0:
		await message.answer("ID должен положительным числом. Введите ID транзакции:", reply_markup=admin_cancel_keyboard())
		return

	transaction = await billing_repo.get_by_id(transaction_id)
	if not transaction:
		await state.clear()
		await message.answer(f"Транзакция с ID={transaction_id} не найдена.", reply_markup=to_billing_control_keyboard())
		return

	await state.update_data(transaction_id=transaction_id)
	user = await user_repo.get_by_id(transaction.user_id)

	msg = (
		f"<code>"
		f" id | Сумма | Пользователь\n"
		f"{'-' * 35}\n"
		f"{transaction_id:03d} | {transaction.amount: 5d} | {user.name}\n"
		f"{'-' * 35}\n"
		f"❌ Удалить транзакцию?"
		f"</code>"
	)

	# Запрос подтверждения
	await message.answer(msg, reply_markup=admin_confirmation_keyboard())
	await state.set_state(BillingControlStates.confirm)


# Подтверждение удаления получено
@router.callback_query(BillingControlStates.confirm, F.data == "admin_ok")
async def deleting_tx_from_db(callback: CallbackQuery, state: FSMContext):
	log.debug("Подтверждение удаления транзакции получено")

	data = await state.get_data()
	transaction_id = data["transaction_id"]

	success = await billing_repo.delete(transaction_id)
	if success:
		status = f"Транзакция с ID={transaction_id} успешно удалена"
		log.debug(status)
	else:
		status = f"Ошибка при удалении транзакции с ID={transaction_id}"
		log.error(status)

	await callback.answer()
	await callback.message.edit_text(status, reply_markup=to_billing_control_keyboard())
	await state.clear()