# src/telegram/billing_crud.py
from src.telegram.handlers.crud_handler import BaseCRUDHandler
from src.db.repositories import billing_repo, AbstractRepository
from src.core.dto import TransactionAddDTO, TransactionDTO
from src.telegram.keyboards import to_billing_control_keyboard, tx_profile_keyboard
from src.telegram.interface import (
	TX_LIST_HEADER, TX_ROW_TEMPLATE, TX_PROFILE_TEMPLATE,
	ENTER_USER_ID, ENTER_TX_AMOUNT, AMOUNT_INVALID, ID_INVALID
)

class BillingCRUDHandler(BaseCRUDHandler[TransactionAddDTO, TransactionDTO, AbstractRepository]):
    entity_name = "tx"
    repo = billing_repo
    add_dto_class = TransactionAddDTO
    dto_class = TransactionDTO

    list_header = TX_LIST_HEADER
    list_row_template = TX_ROW_TEMPLATE
    profile_template = TX_PROFILE_TEMPLATE
    back_keyboard = to_billing_control_keyboard()
    profile_keyboard = tx_profile_keyboard()

    add_fields = ["user_id", "amount"]
    field_prompts = {
        "user_id": ENTER_USER_ID,
        "amount": ENTER_TX_AMOUNT
    }
    field_validators = {
        "user_id": lambda x: (x.isdigit(), ID_INVALID),
        "amount": lambda x: (x.isdigit() and (a := int(x)) > 0 and a % 100 == 0, AMOUNT_INVALID
        ) if x.isdigit() else (False, AMOUNT_INVALID)
    }

    def get_entity_id(self, item: TransactionDTO) -> int:
        return item.id

    def format_list_row(self, item: TransactionDTO) -> str:
        return self.list_row_template.format(tx_id=item.id, amount=item.amount, name=item.user_id)

    async def resolve_field_value(self, field: str, value: str):
        if field in ("user_id", "amount"):
            return int(value)
        return value

billing_crud = BillingCRUDHandler()