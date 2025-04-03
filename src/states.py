from aiogram.fsm.state import State, StatesGroup


class AddPayment(StatesGroup):
    comment = State()
    created_at = State()
    amount = State()


class DeletePayment(StatesGroup):
    payment_id = State()


class GetPayments(StatesGroup):
    created_at_first = State()
    created_at_second = State()


class UpdatePayment(StatesGroup):
    payment_id = State()
    amount = State()
    comment = State()
