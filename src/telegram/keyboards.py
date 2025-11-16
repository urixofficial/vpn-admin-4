from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.telegram.interface import ADD_BUTTON, EDIT_BUTTON, DELETE_BUTTON, BACK_BUTTON, REGISTER_BUTTON, CANCEL_BUTTON, \
	OK_BUTTON, MAIN_PAGE_BUTTON, USERS_PAGE_BUTTON, BILLING_PAGE_BUTTON, STATS_PAGE_BUTTON, \
	LIST_BUTTON, SHOW_PROFILE_BUTTON


# === Клавиатуры пользователя ===

def user_register_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=REGISTER_BUTTON, callback_data="register"),
			]
		]
	)

def user_cancel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=CANCEL_BUTTON, callback_data="user_cancel"),
			]
		]
	)

def to_user_panel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=USERS_PAGE_BUTTON, callback_data="user_panel"),
			]
		]
	)

def user_confirmation_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=OK_BUTTON, callback_data="user_ok"),
				InlineKeyboardButton(text=CANCEL_BUTTON, callback_data="user_cancel")
			]
		]
	)

# === Клавиатуры админа ===

def admin_cancel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=CANCEL_BUTTON, callback_data="admin_cancel"),
			]
		]
	)

def to_admin_panel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=MAIN_PAGE_BUTTON, callback_data="admin_panel"),
			]
		]
	)

def to_user_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=BACK_BUTTON, callback_data="user_control"),
			]
		]
	)

def to_billing_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=BACK_BUTTON, callback_data="billing_control"),
			]
		]
	)

def admin_confirmation_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=OK_BUTTON, callback_data="admin_ok"),
				InlineKeyboardButton(text=CANCEL_BUTTON, callback_data="admin_cancel")
			]
		]
	)

def admin_panel_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=USERS_PAGE_BUTTON, callback_data="user_control")
			],
			[
				InlineKeyboardButton(text=BILLING_PAGE_BUTTON, callback_data="billing_control")
			],
			[
				InlineKeyboardButton(text=STATS_PAGE_BUTTON, callback_data="system_stats")
			]
		]
	)

def user_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=LIST_BUTTON, callback_data="user_list"),
			],
			[
				InlineKeyboardButton(text=SHOW_PROFILE_BUTTON, callback_data="user_show")
			],
			[
				InlineKeyboardButton(text=ADD_BUTTON, callback_data="user_add"),
			],
			[
				InlineKeyboardButton(text=MAIN_PAGE_BUTTON, callback_data="admin_panel")
			]

		]
	)

def billing_control_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=LIST_BUTTON, callback_data="tx_list"),
			],
			[
				InlineKeyboardButton(text=SHOW_PROFILE_BUTTON, callback_data="tx_show"),
			],
			[
				InlineKeyboardButton(text=ADD_BUTTON, callback_data="tx_add"),
			],
			[
				InlineKeyboardButton(text=BACK_BUTTON, callback_data="admin_panel")
			]

		]
	)

def user_profile_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=EDIT_BUTTON, callback_data="user_edit"),
				InlineKeyboardButton(text=DELETE_BUTTON, callback_data="user_delete")
			],
			[
				InlineKeyboardButton(text=BACK_BUTTON, callback_data="user_control")
			]

		]
	)

def tx_profile_keyboard():
	return InlineKeyboardMarkup(
		inline_keyboard=[
			[
				InlineKeyboardButton(text=EDIT_BUTTON, callback_data="tx_edit"),
				InlineKeyboardButton(text=DELETE_BUTTON, callback_data="tx_delete")
			],
			[
				InlineKeyboardButton(text=BACK_BUTTON, callback_data="tx_control")
			]

		]
	)