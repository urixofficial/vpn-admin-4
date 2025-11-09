from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


def cancel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Отмена", callback_data="cancel"),
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

def confirmation_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="OK", callback_data="ok"),
				InlineKeyboardButton(text="Отмена", callback_data="cancel")
			]
		]
	)

def admin_panel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Пользователи", callback_data="user_control")
			],
			[
				InlineKeyboardButton(text="Транзакции", callback_data="transaction_control")
			],
			[
				InlineKeyboardButton(text="Статистика", callback_data="system_stats")
			]
		]
	)

def user_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text="Список", callback_data="user_list"),
				InlineKeyboardButton(text="Инфо", callback_data="user_info")
			],
			[
				InlineKeyboardButton(text="Добавить", callback_data="user_add"),
				InlineKeyboardButton(text="Изменить", callback_data="user_edit"),
				InlineKeyboardButton(text="Удалить", callback_data="user_delete")
			],
			[
				InlineKeyboardButton(text="Назад", callback_data="admin_panel")
			]

		]
	)