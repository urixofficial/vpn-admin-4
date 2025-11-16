# src/telegram/messages.py

from typing import Final

# === Кнопки ===
REGISTER_BUTTON: Final = "Зарегистрироваться"
OK_BUTTON: Final = "OK"
CANCEL_BUTTON: Final = "Отмена"
BACK_BUTTON: Final = "🔙 Назад"
MAIN_PAGE_BUTTON: Final = "На главную"
USERS_PAGE_BUTTON: Final = "👤 Пользователи"
BILLING_PAGE_BUTTON: Final = "💰 Биллинг"
STATS_PAGE_BUTTON: Final = "📊 Статистика"
LIST_BUTTON: Final = "📋 Список"
SHOW_PROFILE_BUTTON: Final = "🔍️ Профиль"
ADD_BUTTON: Final = "➕ Добавить"
EDIT_BUTTON: Final = "✏️ Изменить"
DELETE_BUTTON: Final = "❌ Удалить"

# === Админ-панель ===
ADMIN_PANEL_TITLE: Final = "Панель администратора:"
USER_CONTROL_TITLE: Final = "Управление пользователями:"
BILLING_CONTROL_TITLE: Final = "Управление биллингом:"


# === В разработке ===
FEATURE_IN_DEV: Final = "Функция в разработке"

# === Общие ===
ACTION_CANCELED: Final = "Действие отменено."
ACCESS_DENIED: Final = "Доступ запрещён."
INVALID_ID: Final = "Некорректный ID. Повторите ввод:"
NOT_FOUND: Final = "Запись не найдена."
INVALID_VALUE: Final = "Неверное значение."
ENTER_ID: Final = "Введите ID:"
LIST_EMPTY: Final = "Список пуст."

# === Поля при добавлении ===
ENTER_USER_ID: Final = "Введите ID пользователя:"
ENTER_USER_NAME: Final = "Введите имя пользователя:"
ENTER_TX_AMOUNT: Final = "Введите сумму транзакции:"

# === Валидация ===
ID_INVALID: Final = "ID должен быть целым положительным числом. Повторите ввод:"
NAME_INVALID: Final = "Имя должно быть от 3 до 25 символов. Повторите ввод:"
NAME_NOT_UNIQUE: Final = "Имя не уникально. Повторите ввод:"
AMOUNT_INVALID: Final = "Сумма должна быть положительным числом, кратным 100 рублям."

# === CRUD ===
DELETE_CONFIRM = (
	"\n"
	"-----------------------------------\n"
	f"Удалить запись?"
)
DELETE_SUCCESS: Final = "✅ Запись успешно удалена."
DELETE_ERROR: Final = "❌ Ошибка при удалении записи."
ADD_SUCCESS: Final = "\n✅ Запись успешно добавлена."
ADD_ERROR: Final = "\n❌ Ошибка при добавлении записи."
UPDATE_SUCCESS: Final = "\n✅ Запись успешно обновлена."
UPDATE_ERROR: Final = "\n❌ Ошибка при обновлении записи."

# === Списки ===
USER_LIST_HEADER: Final = (
	"Список пользователей:\n"
	"-----------------------------------\n"
)
USER_LIST_STATUS_ACTIVE: Final = "✅"
USER_LIST_STATUS_INACTIVE: Final = "❌"
USER_LIST_ROW: Final = "{status} {name} ({user_id})\n"
TX_LIST_HEADER: Final = (
	"📋 Список транзакций:\n"
	"-----------------------------------\n"
)
TX_ROW_TEMPLATE: Final = "🆔 {tx_id:03d}  💰{amount: 5d}  👤 {name}\n"

# === Профили ===
USER_PROFILE_TEMPLATE: Final = (
    "<b>{name}</b>\n"
    "-----------------------------------\n"
    "🆔 {id}\n"
    "🚫 {blocked}\n"
    "🗓️ {billing_start_date}\n"
    "🗓️ {billing_end_date}\n"
)

TX_PROFILE_TEMPLATE: Final = (
    "<b>Транзакция {id}</b>\n"
    "-----------------------------------\n"
    "Сумма: {amount}\n"
    "ID пользователя: {user_id}\n"
    "Создана: {created_at}\n"
    "Обновлена: {updated_at}\n"
)

# === Регистрация ===
USER_NOT_REGISTERED: Final = "⚠️ Вы не зарегистрированы."
REG_USER_CONFIRM: Final = "🛎️ Отправить запрос администратору?"
REG_ADMIN_CONFIRM: Final = ("{name} ({user_id})\n\n"
                            "🛎️ Запрос на регистрацию:")
REG_REQUEST_SENT: Final = "ℹ️ Запрос отправлен администратору."
REG_SUCCESS_ADMIN: Final = "✅ Пользователь успешно добавлен."
REG_SUCCESS_USER: Final = "✅ Подтверждение получено. Вы успешно зарегистрированы!"
REG_ERROR_ADMIN: Final = "❌ Ошибка добавления пользователя в базу."
REG_ERROR_USER: Final = "❌ Возникла ошибка при регистрации."
REG_REJECTED_ADMIN: Final = "❌ Регистрация пользователя {user_id} отклонена."
REG_REJECTED_USER: Final = "❌ Администратор отклонил ваш запрос."


# =====================================================================================================================
# =============================================== Статистика ==========================================================
# =====================================================================================================================

STATS_TEMPLATE: Final = (
    "Системная статистика:\n\n"
    "👤 Всего пользователей: {users_total_count}\n"
    "✅ Активных: {users_active}\n"
    "⌛ Просроченных: {users_expired}\n"
    "❌ Заблокированных: {users_blocked}\n\n"
	"📋 Всего транзакций: {tx_total_count}\n"
	"💰 Сумма транзакций: {tx_total_amount}"
)