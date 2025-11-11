from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


def user_register_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Зарегистрироваться", callback_data="register"),
			]
		]
	)

def admin_cancel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Отмена", callback_data="admin_cancel"),
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

def user_confirmation_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="OK", callback_data="user_ok"),
				InlineKeyboardButton(text="Отмена", callback_data="user_cancel")
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
				InlineKeyboardButton(text="🔍️ Показать профиль", callback_data="user_choose")
			],
			[
				InlineKeyboardButton(text="➕ Добавить нового", callback_data="user_add"),
			],
			[
				InlineKeyboardButton(text="🔙 На главную", callback_data="admin_panel")
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
				InlineKeyboardButton(text="➕️ Добавить", callback_data="tx_add"),
				# InlineKeyboardButton(text="✏️ Изменить", callback_data="tx_edit"),
				InlineKeyboardButton(text="❌ Удалить", callback_data="tx_delete")
			],
			[
				InlineKeyboardButton(text="🔙 Назад", callback_data="admin_panel")
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