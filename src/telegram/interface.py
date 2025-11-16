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

# === В разработке ===
FEATURE_IN_DEV: Final = "Функция в разработке"

# Вспомогательная строка-разделитель
SEP: Final = "-" * 35

# === Общие ===
ACTION_CANCELED: Final = "Действие отменено"
ACCESS_DENIED: Final = "Доступ запрещён."

# === Админ-панель ===
ADMIN_PANEL_TITLE: Final = "Панель администратора:"
USER_CONTROL_TITLE: Final = "Управление пользователями:"
BILLING_CONTROL_TITLE: Final = "Управление биллингом:"

# =====================================================================================================================
# ============================================= Пользователи ==========================================================
# =====================================================================================================================

# === Запрос информации ===
ENTER_USER_ID: Final = "Введите ID пользователя:"
ENTER_NAME: Final = "Введите имя пользователя:"
USER_DELETE_CONFIRM: Final = "⚠️ Удалить пользователя {name} ({user_id})?"

# === Валидация ===
NAME_NOT_UNIQUE: Final = "⚠️ Имя не уникально. Введите другое имя:"
NAME_EMPTY: Final = "⚠️ Имя не может быть пустым. Введите имя пользователя:"
NAME_TOO_LONG: Final = "⚠️ Имя должно быть не длиннее 25 символов. Введите имя пользователя:"
USER_ID_NOT_NUMBER: Final = "⚠️ ID должен быть числом. Введите ID пользователя:"
USER_EXISTS: Final = "⚠️ Пользователь с указанным ID уже существует."
USER_NOT_FOUND: Final = "⚠️ Пользователь с указанным ID не найден."

# === Список пользователей ===
USER_LIST_EMPTY: Final = "Нет пользователей."
USER_LIST_HEADER: Final = "Список пользователей:\n\n"
USER_LIST_STATUS_ACTIVE: Final = "✅"
USER_LIST_STATUS_INACTIVE: Final = "❌"
USER_LIST_ROW: Final = "{status} {name} ({user_id})\n"

# === Профиль пользователя ===
USER_PROFILE_TEMPLATE: Final = (
    "<b>{name}</b>\n"
    "-----------------------------------\n"
    "🆔 {id}\n"
    "🚫 {blocked}\n"
    "🗓️ {billing_start_date}\n"
    "🗓️ {billing_end_date}\n"
)

# === Статусы ===
USER_ADDED_SUCCESS: Final = "✅ Пользователь успешно добавлен."
USER_ADDED_ERROR: Final = "❌ Ошибка при добавлении пользователя."
USER_DELETED_SUCCESS: Final = "✅ Пользователь успешно удален."
USER_DELETED_ERROR: Final = "❌ Ошибка при удалении пользователя."

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
# ============================================= Транзакции ============================================================
# =====================================================================================================================

# === Список транзакций ===
TX_LIST_EMPTY: Final = "Нет транзакций."
TX_LIST_HEADER: Final = "📋 Список транзакций:\n\n"
TX_ROW_TEMPLATE: Final = "🆔 {tx_id:03d}  💰{amount: 5d}  👤 {name}\n"

# === Профиль пользователя ===
TX_PROFILE_TEMPLATE: Final = (
    "<b>Транзакция {id}</b>\n"
    "-----------------------------------\n"
    "Сумма: {amount}\n"
    "ID пользователя: {user_id}\n"
    "Создана: {created_at}\n"
    "Обновлена: {updated_at}\n"
)

# === Запро информации ===
ENTER_TX_ID: Final = "Введите ID транзакции:"
ENTER_AMOUNT: Final = "Введите сумму транзакции"
TX_DELETE_CONFIRM: Final = TX_ROW_TEMPLATE + "\n⚠️ Удалить транзакцию?"

# === Валидация ===
TX_ID_NOT_NUMBER: Final = "⚠️ ID должен быть целым числом. Введите ID транзакции:"
TX_ID_NOT_POSITIVE: Final = " ⚠️ ID должен положительным числом. Введите ID транзакции:"
AMOUNT_INVALID: Final = "⚠️ Сумма должна быть целым числом.\nВведите сумму транзакции:"
AMOUNT_INVALID_RULE: Final = "⚠️ Сумма должна быть больше нуля и кратна 100 рублям.\nВведите сумму транзакции:"
TX_NOT_FOUND: Final = "⚠️ Транзакция {tx_id} не найдена."

# === Статусы ===
TX_ADDED_SUCCESS: Final = TX_ROW_TEMPLATE + "\n✅ Транзакция успешно добавлена."
TX_ADDED_ERROR: Final = TX_ROW_TEMPLATE + "\n❌ Ошибка при добавлении транзакции."
TX_DELETED_SUCCESS: Final = "✅ Транзакция успешно удалена."
TX_DELETED_ERROR: Final = "❌ Ошибка при удалении транзакции."


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