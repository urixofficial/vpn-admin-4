from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.core.config import settings
from src.core.dto import UserStatus
from src.core.logger import log
from src.db.repositories import user_repo, billing_repo
from src.telegram.interface import ACTION_CANCELED, ACCESS_DENIED, ADMIN_PANEL_TITLE, USER_CONTROL_TITLE, \
	BILLING_CONTROL_TITLE, STATS_TEMPLATE

from src.telegram.keyboards import (admin_panel_keyboard, user_control_keyboard, billing_control_keyboard,
                                    to_admin_panel_keyboard)


router = Router(name="admin_handler")

# Проверка на админа
def is_admin(obj: Message | CallbackQuery) -> bool:
	return obj.from_user.id == settings.TELEGRAM_ADMIN_ID


# Отмена текущего действия
@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(callback: CallbackQuery, state: FSMContext):
	log.debug("Отмена действия")

	await callback.answer()
	await state.clear()
	await callback.message.edit_text(ACTION_CANCELED, reply_markup=to_admin_panel_keyboard())


# Вывод панели администратора
@router.message(Command("admin"))
@router.callback_query(F.data == "admin_panel")
async def admin_panel(update: Message | CallbackQuery, state: FSMContext):
	log.debug("Вывод панели администратора")

	if not is_admin(update):
		await update.answer(ACCESS_DENIED)
		return

	await state.clear()

	if isinstance(update, Message):
		await update.answer(ADMIN_PANEL_TITLE, reply_markup=admin_panel_keyboard())
	elif isinstance(update, CallbackQuery):
		await update.answer()
		await update.message.edit_text(ADMIN_PANEL_TITLE, reply_markup=admin_panel_keyboard())


# Вывод панели управления пользователями
@router.callback_query(F.data == "user_control")
async def cb_user_control(callback: CallbackQuery):
	log.debug("Вывод управления пользователями")

	await callback.answer()
	await callback.message.edit_text(USER_CONTROL_TITLE, reply_markup=user_control_keyboard())


# Вывод панели управления транзакциями
@router.callback_query(F.data == "billing_control")
async def cb_billing_control(callback: CallbackQuery):
	log.debug("Вывод управления биллингом")

	await callback.answer()
	await callback.message.edit_text(BILLING_CONTROL_TITLE, reply_markup=billing_control_keyboard())


# Вывод системной статистики
@router.callback_query(F.data == "system_stats")
async def cb_system_stats(callback: CallbackQuery):
	log.debug("Вывод системной статистики")

	users_total, active, expired, blocked = 0, 0, 0, 0

	users = await user_repo.get_all()
	if users:
		users_total = len(users)
		for user in users:
			match user.status:
				case UserStatus.BLOCKED:
					blocked += 1
				case UserStatus.ACTIVE:
					active +=1
				case UserStatus.EXPIRED:
					expired +=1

	tx_total_count, tx_total_amount = 0, 0

	transactions = await billing_repo.get_all()
	if transactions:
		tx_total_count = len(transactions)
		tx_total_amount = sum([tx.amount for tx in transactions])

	stats = STATS_TEMPLATE.format(
		users_total_count=users_total,
		users_active=active,
		users_expired=expired,
		users_blocked=blocked,
		tx_total_count=tx_total_count,
		tx_total_amount=tx_total_amount
	)

	await callback.answer()
	await callback.message.edit_text(stats, reply_markup=to_admin_panel_keyboard())