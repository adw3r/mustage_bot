import os
import uuid

import pandas
from aiogram import Router
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from src import keyboards, schemas
from src.config import REPORTS_FOLDER
from src.interfaces import Api
from src.log import logger
from src.states import AddPayment, DeletePayment, GetPayments, UpdatePayment

router = Router()
class MyFilter(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text

# /start command
@router.message(Command('start'))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я бот для учета расходов. Выбери действие:", reply_markup=keyboards.main_menu()
    )
    return

# Get payment
@router.message(MyFilter(my_text='Получить отчет'))
async def get_payments(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return
    await message.answer(
        "Введите дату с которой формировать отчет формата dd.mm.yyyy:", reply_markup=keyboards.back_to_menu()
    )
    await state.set_state(GetPayments.created_at_first)
    return


@router.message(GetPayments.created_at_first)
async def get_payments_created_at_first(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return
    await message.answer(
        "Введите дату по которую формировать отчет формата dd.mm.yyyy:",
        reply_markup=keyboards.back_to_menu(),
    )
    await state.update_data(created_at_first=message.text)
    await state.set_state(GetPayments.created_at_second)
    return


@router.message(GetPayments.created_at_second)
async def get_payments_created_at_second(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return
    await state.update_data(created_at_second=message.text)
    await message.answer(
        "Формирую отчет",
        reply_markup=keyboards.back_to_menu(),
    )
    try:
        user_data = await state.get_data()
        get_payments_schema = schemas.GetPayments(**user_data)
        get_payments_response = await Api.get_payments_with_dates(get_payments_schema)
        assert get_payments_response.is_success

        frame = pandas.DataFrame(get_payments_response.json())
        filename = (f"report_" \
                 f"{uuid.uuid4()}_" \
                 f"{get_payments_schema.created_at_first}_" \
                 f"{get_payments_schema.created_at_second}.xlsx")
        filename_path = REPORTS_FOLDER / filename
        frame.to_excel(filename_path, index=False)
        document = FSInputFile(filename_path, filename=filename)
        await state.clear()
        await message.answer_document(document, reply_markup=keyboards.main_menu())
        os.remove(filename_path)
    except Exception as error:
        logger.exception(error)
        await message.answer(
            "❌ Неизвестная ошибка!", reply_markup=keyboards.back_to_menu()
        )
    await state.clear()
    return

# Delete payment
@router.message(MyFilter(my_text='Удалить расход'))
async def delete_expense_start(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return

    await message.answer(f"Введите ID расхода для удаления:", reply_markup=keyboards.back_to_menu())
    await state.update_data(payment_id=message.text)
    await state.set_state(DeletePayment.payment_id)
    return


@router.message(DeletePayment.payment_id)
async def delete_expense_confirm(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return
    try:
        payment_id = int(message.text)
        delete_payment_response = await Api.delete_payment(payment_id)

        if delete_payment_response.status_code == 200:
            await message.answer(
                f"✅ Расход {payment_id} удален!", reply_markup=keyboards.main_menu()
            )
        else:
            await message.answer("❌ Ошибка! Расход не найден.", reply_markup=keyboards.main_menu())
    except ValueError:
        await message.answer("❌ Ошибка! Введите числовой ID.", reply_markup=keyboards.main_menu())
    except Exception as error:
        logger.error(error)
        await message.answer("❌ Неизвестная ошибка!", reply_markup=keyboards.main_menu())
    finally:
        await state.clear()
        return

# Add payment
@router.message(MyFilter(my_text='Добавить расход'))
async def add_expense_start(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return

    await message.answer("Введите название расхода:", reply_markup=keyboards.back_to_menu())
    await state.set_state(AddPayment.comment)
    return



@router.message(AddPayment.comment)
async def add_expense_name(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return

    await state.update_data(comment=message.text)
    await message.answer("Введите дату расхода в формате dd.mm.yyyy:", reply_markup=keyboards.back_to_menu())
    await state.set_state(AddPayment.created_at)
    return


@router.message(AddPayment.created_at)
async def add_expense_date(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return

    await state.update_data(created_at=message.text)
    await message.answer("Введите сумму расхода (в грн):", reply_markup=keyboards.back_to_menu())
    await state.set_state(AddPayment.amount)
    return


async def transform_to_numeric(amount_uah):
    try:
        amount_uah = float(amount_uah.replace(",", "."))  # Конвертация запятой в точку
    except Exception as error:
        logger.error(error)
        amount_uah = None
    return amount_uah


@router.message(AddPayment.amount)
async def add_expense_amount(message: Message, state: FSMContext):
    if await back_to_menu(message, state):
        return
    try:
        amount_uah = None
        amount_uah = await transform_to_numeric(message.text)
        if not amount_uah:
            await message.answer(
                "Ошибка ввода. Расход должен может быть в формете 1312, 1312.11, 1312.132",
                reply_markup=keyboards.main_menu(),
            )
            return

        await state.update_data(amount_uah=amount_uah)
        user_data = await state.get_data()
        payment = schemas.PaymentCreate(**user_data)
        add_payment_response = await Api.add_payment(payment)
        logger.info(f'{add_payment_response = }')
        if add_payment_response.is_success:
            await message.answer(
                f"✅ Расход добавлен: {user_data['comment']} — {amount_uah} грн",
                reply_markup=keyboards.main_menu(),
            )
        else:
            logger.error(f'{add_payment_response.text = }')
    except Exception as error:
        logger.error(error)
        await message.answer("❌ Ошибка!", reply_markup=keyboards.main_menu())
    finally:
        await state.clear()
        return

# Update payment
@router.message(MyFilter(my_text="Изменить расход"))
async def update_payment_start_state(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return

    try:
        get_payments_response = await Api.get_payments()
        assert get_payments_response.is_success
        frame = pandas.DataFrame(get_payments_response.json())
        filename = (
            f"all_dates_report_{uuid.uuid4()}.xlsx"
        )
        filename_path = REPORTS_FOLDER / filename
        frame.to_excel(filename_path, index=False)
        document = FSInputFile(filename_path, filename=filename)
        await message.answer_document(document, reply_markup=keyboards.main_menu())
        os.remove(filename_path)

        await message.answer(
            f"Введите ID расхода для изменения:", reply_markup=keyboards.back_to_menu()
        )
        await state.set_state(UpdatePayment.payment_id)
    except Exception as error:
        logger.exception(error)
    return


@router.message(UpdatePayment.payment_id)
async def update_after_payment_id(message: Message, state: FSMContext):
    if await back_to_menu(message, state):
        return

    response = await Api.get_payment_by_id(message.text)
    if response.is_success:
        await state.update_data(payment_id=message.text)
        try:
            await message.answer("Введите название расхода:", reply_markup=keyboards.back_to_menu())
        except Exception as error:
            logger.exception(error)
        await state.set_state(UpdatePayment.comment)
    else:
        await message.answer('Ошибка! Платёж не найден', reply_markup=keyboards.main_menu())
        await state.clear()

    return


@router.message(UpdatePayment.comment)
async def update_after_comment(message: Message, state: FSMContext):
    if await back_to_menu(message, state):return
    await state.update_data(comment=message.text)

    try:
        await message.answer("Введите сумму расхода (в грн):", reply_markup=keyboards.back_to_menu())

    except Exception as error:
        logger.exception(error)
    await state.set_state(UpdatePayment.amount)
    return


@router.message(UpdatePayment.amount)
async def update_after_amount(message: Message, state: FSMContext):
    if await back_to_menu(message, state):
        return

    try:
        amount_uah = None
        amount_uah = await transform_to_numeric(message.text)
        if not amount_uah:
            await message.answer(
                "Ошибка ввода. Расход должен может быть в формете 1312, 1312.11, 1312.132",
                reply_markup=keyboards.main_menu(),
            )
            return

        await state.update_data(amount_uah=amount_uah)
        user_data = await state.get_data()
        payment = schemas.PaymentPatch(**user_data)
        add_payment_response = await Api.patch_payment(payment)
        logger.info(f"{add_payment_response = }")
        if add_payment_response.is_success:
            await message.answer(
                f"✅ Расход изменён: {user_data['comment']} — {amount_uah} грн",
                reply_markup=keyboards.main_menu(),
            )
        else:
            logger.error(f'{add_payment_response.text = }')
    except Exception as error:
        logger.exception(error)
    await state.clear()
    return

# Back to manu
@router.message(MyFilter(my_text="Назад в меню"))
async def get_back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вы снова в меню", reply_markup=keyboards.main_menu()
    )
    return


async def back_to_menu(message, state):
    if message.text == "Назад в меню":
        await state.clear()
        await message.answer(
            "Выбери действие:",
            reply_markup=keyboards.main_menu(),
        )
        return True
