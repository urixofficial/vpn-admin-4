from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.core.config import settings
from src.core.dto import UserStatus
from src.core.logger import log
from src.db.repositories import user_repo, billing_repo

from src.telegram.keyboards import (admin_panel_keyboard, user_control_keyboard, billing_control_keyboard,
                                    to_admin_panel_keyboard)


router = Router(name="admin_handler")


def is_admin(obj: Message | CallbackQuery) -> bool:
	return obj.from_user.id == settings.TELEGRAM_ADMIN_ID


# Отмена текущего действия
@router.callback_query(F.data == "admin_cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
	log.debug("Отмена действия")

	await callback.answer()
	await state.clear()
	await callback.message.edit_text("Действие отменено", reply_markup=to_admin_panel_keyboard())


# Вывод панели администратора
@router.message(Command("admin"))
@router.callback_query(F.data == "admin_panel")
async def admin_panel(update: Message | CallbackQuery):
	log.debug("Вывод панели администратора")

	if not is_admin(update):
		await update.answer("Доступ запрещён.")
		return

	if isinstance(update, Message):
		await update.answer("Панель администратора:", reply_markup=admin_panel_keyboard())
	elif isinstance(update, CallbackQuery):
		await update.answer()
		await update.message.edit_text("Панель администратора:", reply_markup=admin_panel_keyboard())


# Вывод панели управления пользователями
@router.callback_query(F.data == "user_control")
async def cb_user_control(callback: CallbackQuery):
	log.debug("Вывод управления пользователями")

	await callback.answer()
	await callback.message.edit_text("Управление пользователями:", reply_markup=user_control_keyboard())


# Вывод панели управления транзакциями
@router.callback_query(F.data == "billing_control")
async def cb_billing_control(callback: CallbackQuery):
	log.debug("Вывод управления биллингом")

	await callback.answer()
	await callback.message.edit_text("Управление биллингом:", reply_markup=billing_control_keyboard())


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

	stats =(f"Системная статистика:\n\n"
	        f"👤 Всего пользователей: {users_total}\n"
	        f"✅ Активных: {active}\n"
			f"⌛ Просроченных: {expired}\n"
			f"❌ Заблокированных: {blocked}\n\n"
			f"📋 Всего транзакций: {tx_total_count}\n"
			f"💰 Сумма транзакций: {tx_total_amount}")

	await callback.answer()
	await callback.message.edit_text(stats, reply_markup=to_admin_panel_keyboard())