from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from src.telegram.interface import ADD_BUTTON, EDIT_BUTTON, DELETE_BUTTON, BACK_BUTTON


# === Клавиатуры пользователя ===

def user_register_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Зарегистрироваться", callback_data="register"),
			]
		]
	)

def user_cancel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Отмена", callback_data="user_cancel"),
			]
		]
	)

def to_user_panel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Панель пользователя", callback_data="user_panel"),
			]
		]
	)

def user_confirmation_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="OK", callback_data="user_ok"),
				InlineKeyboardButton(text="Отмена", callback_data="user_cancel")
			]
		]
	)

# === Клавиатуры админа ===

def admin_cancel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Отмена", callback_data="admin_cancel"),
			]
		]
	)

def to_admin_panel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="На главную", callback_data="admin_panel"),
			]
		]
	)

def to_user_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Назад", callback_data="user_control"),
			]
		]
	)

def to_billing_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Назад", callback_data="billing_control"),
			]
		]
	)

def admin_confirmation_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="OK", callback_data="admin_ok"),
				InlineKeyboardButton(text="Отмена", callback_data="admin_cancel")
			]
		]
	)

def admin_panel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="👤 Пользователи", callback_data="user_control")
			],
			[
				InlineKeyboardButton(text="💰 Биллинг", callback_data="billing_control")
			],
			[
				InlineKeyboardButton(text="📊 Статистика", callback_data="system_stats")
			]
		]
	)

def user_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="📋 Список пользователей", callback_data="user_list"),
			],
			[
				InlineKeyboardButton(text="🔍️ Показать профиль", callback_data="user_show")
			],
			[
				InlineKeyboardButton(text="➕ Добавить нового", callback_data="user_add"),
			],
			[
				InlineKeyboardButton(text="🔙 На главную", callback_data="admin_panel")
			]

		]
	)

def user_profile_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				# InlineKeyboardButton(text=EDIT_BUTTON, callback_data=f"edit_user_{user.id}"),
				InlineKeyboardButton(text=DELETE_BUTTON, callback_data=f"user_delete")
			],
			[
				InlineKeyboardButton(text=BACK_BUTTON, callback_data="user_control")
			]

		]
	)

def billing_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="📋 Список транзакций", callback_data="tx_list"),
			],
			[
				InlineKeyboardButton(text="📋 Показать профиль", callback_data="tx_show"),
			],
			[
				InlineKeyboardButton(text="➕️ Добавить", callback_data="tx_add"),
			],
			[
				InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")
			]

		]
	)

def tx_profile_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=DELETE_BUTTON, callback_data=f"tx_delete")
			],
			[
				InlineKeyboardButton(text=BACK_BUTTON, callback_data="billing_control")
			]

		]
	)