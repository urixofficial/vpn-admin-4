from datetime import date

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
	Message, InlineKeyboardMarkup, InlineKeyboardButton,
	CallbackQuery
)

from src.core.config import settings
from src.core.logger import log

from src.telegram.keyboards import (cancel_keyboard, admin_panel_keyboard, user_control_keyboard,
                                    confirmation_keyboard, to_user_control_keyboard)

router = Router(name="admin_handler")


def is_admin(message: Message) -> bool:
	return message.from_user.id == settings.TELEGRAM_ADMIN_ID

@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
	log.debug("Отмена операции")
	await callback.answer()
	await state.clear()
	await callback.message.edit_text("Действие отменено", reply_markup=to_user_control_keyboard())


@router.message(Command("admin"))
async def admin_panel(message: Message):
	log.debug("Вывод панели администратора")
	if not is_admin(message):
		await message.answer("Доступ запрещён.")
		return
	await message.answer("Панель администратора:", reply_markup=admin_panel_keyboard())


@router.callback_query(F.data == "user_control")
async def cb_user_control(callback: CallbackQuery):
	log.debug("Вывод управления пользователями")
	await callback.answer()
	await callback.message.edit_text("Управление пользователями:", reply_markup=user_control_keyboard())

