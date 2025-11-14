from datetime import datetime, date

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.core.logger import log
from src.core.dto import UserDTO, UserStatus, TransactionAddDTO, TransactionDTO
from src.db.repositories import user_repo, billing_repo
from src.telegram.interface import TX_LIST_EMPTY, TX_LIST_HEADER, TX_ROW_TEMPLATE, ENTER_USER_ID, USER_ID_NOT_NUMBER, \
	USER_NOT_FOUND, ENTER_AMOUNT, AMOUNT_INVALID, AMOUNT_INVALID_RULE, TX_ADDED_SUCCESS, TX_ADDED_ERROR, FEATURE_IN_DEV, \
	ENTER_TX_ID, TX_ID_NOT_NUMBER, TX_ID_NOT_POSITIVE, TX_NOT_FOUND, TX_DELETE_CONFIRM, TX_DELETED_SUCCESS, \
	TX_DELETED_ERROR, TX_PROFILE_TEMPLATE, SEP, DELETE_BUTTON, BACK_BUTTON

from src.telegram.keyboards import (admin_cancel_keyboard, admin_confirmation_keyboard,
                                    to_billing_control_keyboard, tx_profile_keyboard)


router = Router(name="billing_control_handler")

class BillingControlStates(StatesGroup):
	enter_user_id = State()
	enter_tx_id = State()
	enter_tx_amount = State()
	confirm_tx_delete = State()


# Вывод списка транзакций
@router.callback_query(F.data == "tx_list")
async def show_tx_list(callback: CallbackQuery):
	log.debug("Вывод списка транзакций")

	transactions = await billing_repo.get_all()
	if not transactions:
		await callback.answer()
		await callback.message.edit_text(TX_LIST_EMPTY, reply_markup=to_billing_control_keyboard())
		return

	tx_list = TX_LIST_HEADER

	for tx in transactions:
		user = await user_repo.get_by_id(tx.user_id)
		name = user.name if user else tx.user_id
		tx_list += TX_ROW_TEMPLATE.format(tx_id=tx.id, amount=tx.amount, name=name)

	await callback.answer()
	await callback.message.edit_text(tx_list, reply_markup=to_billing_control_keyboard())


# Вывод профиля транзакции
async def show_tx_info(message: Message, state: FSMContext, tx: TransactionDTO):
	log.debug("Вывод информации о транзакции")

	user = await user_repo.get_by_id(tx.user_id)
	name = user.name if user else tx.user_id

	tx_profile = TX_PROFILE_TEMPLATE.format(
		tx_id=tx.id,
		name=name,
		amount=tx.amount,
		created_at=tx.created_at,
		updated_at=tx.updated_at,
		sep=SEP
	)

	await message.answer(tx_profile, reply_markup=tx_profile_keyboard())
	await state.update_data(tx_id=tx.id) # для передачи ID в хэндлеры CRUD-операций


# Ввод ID транзакции
@router.callback_query(F.data == "tx_show")
async def ask_tx_id(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос ID транзакции")

	await callback.answer()
	await callback.message.edit_text(ENTER_TX_ID, reply_markup=admin_cancel_keyboard())
	await state.set_state(BillingControlStates.enter_tx_id)


# Проверка ID транзакции и вывод информации о ней
@router.message(BillingControlStates.enter_tx_id)
async def check_tx_id(message: Message, state: FSMContext):
	log.debug("Проверка ID транзакции")

	# Валидация ID
	try:
		tx_id = int(message.text)
	except ValueError:
		await message.answer(TX_ID_NOT_NUMBER, reply_markup=admin_cancel_keyboard())
		return

	if tx_id <= 0:
		await message.answer(TX_ID_NOT_POSITIVE, reply_markup=admin_cancel_keyboard())
		return

	# Получение транзакции из базы данных
	tx = await billing_repo.get_by_id(tx_id)
	if not tx:
		await state.clear()
		await message.answer(TX_NOT_FOUND.format(tx_id=tx_id), reply_markup=to_billing_control_keyboard())
		return

	await state.update_data(transaction_id=tx_id) # Сохранение ID в буфер для CRUD-операций
	await show_tx_info(message, state, tx)


# =====================================================================================================================
# ================================================ CRUD ===============================================================
# =====================================================================================================================

# Добавление транзакции. Запрос ID пользователя
@router.callback_query(F.data == "tx_add")
async def ask_user_id(callback: CallbackQuery, state: FSMContext):
	log.debug("Запрос ID пользователя")

	await callback.answer()
	await callback.message.edit_text(ENTER_USER_ID, reply_markup=to_billing_control_keyboard())
	await state.set_state(BillingControlStates.enter_user_id)


# Добавление транзакции. Проверка ID пользователя
@router.message(BillingControlStates.enter_user_id)
async def check_user_id(message: Message, state: FSMContext):
	log.debug("Проверка ID пользователя")

	# Валидация ID
	try:
		user_id = int(message.text)
	except ValueError:
		await message.answer(USER_ID_NOT_NUMBER)
		return

	# Проверка наличия пользователя в базе данных
	user = await user_repo.get_by_id(user_id)
	if not user:
		await message.answer(USER_NOT_FOUND, reply_markup=to_billing_control_keyboard())
		await state.clear()
		return

	# Переход к следующему шагу
	await state.update_data(user_id=user_id)
	await ask_amount(message, state)


# Добавление транзакции. Запрос суммы транзакции
async def ask_amount(message: Message, state: FSMContext):
	log.debug("Запрос суммы транзакции")

	await message.answer(ENTER_AMOUNT, reply_markup=admin_cancel_keyboard())
	await state.set_state(BillingControlStates.enter_tx_amount)


# Добавление транзакции. Проверка суммы транзакции и добавление в БД
@router.message(BillingControlStates.enter_tx_amount)
async def check_amount_save_to_db(message: Message, state: FSMContext):
	log.debug("Проверка суммы транзакции")

	# Валидация суммы
	try:
		amount = int(message.text)
	except ValueError:
		await message.answer(AMOUNT_INVALID,
		                     reply_markup=admin_cancel_keyboard())
		return

	if amount <= 0 or amount % 100 != 0:
		await message.answer(AMOUNT_INVALID_RULE,
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
		msg = TX_ADDED_SUCCESS.format(
			tx_id=transaction_id,
			amount=amount,
			name=user.name
		)
	else:
		log.error(f"Ошибка при добавлении транзакции в базу данных")
		msg = TX_ADDED_ERROR.format(
			tx_id=transaction_id,
			amount=amount,
			name=user.name
		)

	await message.answer(msg, reply_markup=to_billing_control_keyboard())


# Изменение транзакции
@router.callback_query(F.data == "tx_edit")
async def tx_edit(callback: CallbackQuery, state: FSMContext):
	log.debug("Обновление транзакции")

	await callback.answer(FEATURE_IN_DEV)


# Удаление транзакции. Запрос подтверждения
@router.callback_query(F.data == "tx_delete")
async def tx_delete_ask_confirm(callback: CallbackQuery, state: FSMContext):
	data = await state.get_data()
	tx_id = data["tx_id"]
	log.debug(f"Запрос подтверждения на удаление транзакции {tx_id}")

	tx = await billing_repo.get_by_id(tx_id)
	user = await user_repo.get_by_id(tx.user_id)
	name = user.name if user else tx.user_id

	tx_delete_msg = TX_DELETE_CONFIRM.format(
		tx_id=tx_id,
		amount=tx.amount,
		name=name
	)

	await callback.answer()
	await callback.message.edit_text(tx_delete_msg, reply_markup=admin_confirmation_keyboard())
	await state.set_state(BillingControlStates.confirm_tx_delete)


# Удаление транзакции. Подтверждение удаления получено
@router.callback_query(BillingControlStates.confirm_tx_delete, F.data == "admin_ok")
async def deleting_tx_from_db(callback: CallbackQuery, state: FSMContext):
	log.debug("Подтверждение удаления транзакции получено")

	data = await state.get_data()
	tx_id = data["transaction_id"]

	success = await billing_repo.delete(tx_id)
	if success:
		status = TX_DELETED_SUCCESS
		log.debug(status)
	else:
		status = TX_DELETED_ERROR
		log.error(status)

	await callback.answer()
	await callback.message.edit_text(status, reply_markup=to_billing_control_keyboard())
	await state.clear()