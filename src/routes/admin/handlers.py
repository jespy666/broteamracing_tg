from typing import Union, TYPE_CHECKING, TypeVar, List, Dict, Any, Optional

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F

from src.routes.admin.states import NewSideBookingState
from src.keyboards import get_inline_menu, get_reply_markup
from src.middlewares import AdminMiddleware
from src.utils import (
    read_template,
    validate_date,
    get_start_times,
    get_available_time_range,
    validate_amount,
    render_chosen_bikes,
    get_end_time,
    validate_duration,
)
from src.api.manager import APIManager
from src.routes.admin import utils

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
    from aiogram.fsm.context import FSMContext


E = TypeVar("E", bound=Union[Message, CallbackQuery])

admin_router = Router()
admin_router.message.middleware(AdminMiddleware())
admin_router.callback_query.middleware(AdminMiddleware())


@admin_router.message(Command("admin"))
async def admin_menu(
    message: Message,
    is_admin: Union[int, bool],
) -> None:
    """
    Меню для Администраторов.
    """
    if not is_admin:
        msg: str = read_template("admin/restricted")
        await message.answer(msg, parse_mode="HTML")
        return

    markup: "InlineKeyboardMarkup" = get_inline_menu(utils.MENU)
    msg: str = read_template("admin/main")
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")


@admin_router.message(Command("admin_side_booking"))
@admin_router.callback_query(F.data == "admin_side_booking")
async def ask_date(
    event: E,
    state: "FSMContext",
    is_admin: bool,
) -> None:
    """
    Состояние 1. Запрос даты проката.
    """
    message = event if isinstance(event, Message) else event.message
    if not is_admin:
        msg: str = read_template("admin/restricted")
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    msg: str = read_template("admin/new_booking/date")
    await message.answer(msg, parse_mode="HTML")
    await state.set_state(NewSideBookingState.date)


@admin_router.message(NewSideBookingState.date)
async def ask_start(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Запрос времени начала.
    """
    date: str = message.text
    if not validate_date(date):
        msg: str = read_template("errors/incorrect_date")
        await message.answer(msg, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    day_info: List[Dict[str, Any]] = await api.load_day_info(date)
    starts: List[str] = get_start_times(day_info)

    msg = read_template("admin/new_booking/start")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(starts)
    await state.update_data(day_info=day_info, starts=starts, date=date)
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.set_state(NewSideBookingState.start)


@admin_router.message(NewSideBookingState.start)
async def ask_duration(message: Message, state: "FSMContext") -> None:
    """
    Состояние 3. Запрос длительности проката.
    """
    start: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not start in data["starts"]:
        msg = read_template("errors/wrong_time")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(data["starts"])
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    available_hours: List[int] = get_available_time_range(
        data["starts"],
        start,
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(available_hours)
    msg = read_template("admin/new_booking/duration")
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(durations=available_hours, start=start)
    await state.set_state(NewSideBookingState.duration)


@admin_router.message(NewSideBookingState.duration)
async def ask_instructor(message: Message, state: "FSMContext") -> None:
    """
    Состояние 4. Запрос инструктора.
    """
    duration: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not validate_duration(duration, data["durations"]):
        msg = read_template("errors/wrong_duration")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(data["durations"])
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    instructors: Dict[str, int] = await api.get_available_instructors(
        data["date"],
        data["start"],
        int(duration),
    )
    msg = read_template("admin/new_booking/instructor")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(list(instructors.keys()))
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(instructors=instructors, duration=int(duration))
    await state.set_state(NewSideBookingState.client_phone)


@admin_router.message(NewSideBookingState.client_phone)
async def ask_client_phone(message: Message, state: "FSMContext") -> None:
    """
    Состояние 5. Запрос телефона клиента.
    """
    instructor: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if instructor not in list(data["instructors"].keys()):
        msg = read_template("errors/chose", entity="инструктора")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(data["instructors"].keys())
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    msg: str = read_template("admin/new_booking/phone")
    await state.update_data(instructor=data["instructors"][instructor])
    await message.answer(msg, parse_mode="HTML")
    await state.set_state(NewSideBookingState.instructor)


@admin_router.message(NewSideBookingState.instructor)
async def ask_bikes(message: Message, state: "FSMContext") -> None:
    """
    Состояние 5. Запрос байков.
    """
    client_phone: str = message.text
    if not utils.validate_phone_number(client_phone):
        msg: str = read_template("errors/phone")
        await state.set_state(await state.get_state())
        await message.answer(msg, parse_mode="HTML")
        return

    data: Dict[str, Any] = await state.get_data()
    api = APIManager()
    available_bikes: Dict[str, int] = await api.get_available_bikes(
        data["date"],
        data["start"],
        data["duration"],
    )
    msg = read_template("admin/new_booking/bikes1")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        list(available_bikes.keys())
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(
        available_bikes=available_bikes,
        client_phone=client_phone,
    )
    await state.set_state(NewSideBookingState.bikes)


@admin_router.message(NewSideBookingState.bikes)
async def ask_amount(message: Message, state: "FSMContext") -> None:
    """
    Состояние 6. Запрос количества байков.
    """
    bike: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not bike in data["available_bikes"].keys():
        msg: str = read_template("errors/wrong_duration")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(data["available_bikes"].keys())
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    msg: str = read_template("admin/new_booking/amount")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        list(range(1, data["available_bikes"][bike] + 1))
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(bike=bike)
    await state.set_state(NewSideBookingState.amount)


@admin_router.message(NewSideBookingState.amount)
async def checkout_bikes(message: Message, state: "FSMContext") -> None:
    """
    Состояние 7. Проверка количества байков.
    """
    amount: str = message.text
    data: Dict[str, Any] = await state.get_data()
    available_bikes: Dict[str, int] = data["available_bikes"]
    bike: str = data["bike"]
    if not validate_amount(amount, available_bikes[bike]):
        msg: str = read_template("errors/wrong_amount")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(range(data["available_bikes"][data["bike"]]))
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    # Обновляем выбранные байки
    bikes: Optional[Dict[str, int]] = data.get("bikes", {})
    bikes[bike] = int(amount)

    # Удаляем байк из доступных
    for key in bikes:
        available_bikes.pop(key, None)

    msg: str = read_template(
        "admin/new_booking/bikes2",
        bikes=render_chosen_bikes(bikes),
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        ["Завершить", "Выбрать еще байк"]
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(
        bike=None,
        available_bikes=available_bikes,
        bikes=bikes,
    )
    await state.set_state(NewSideBookingState.confirm)


@admin_router.message(NewSideBookingState.confirm)
async def confirm(message: Message, state: "FSMContext") -> None:
    """
    Состояние 7. Создание записи или выбор еще байков.
    """
    action: str = message.text
    actions = ["Завершить", "Выбрать еще байк"]
    data: Dict[str, Any] = await state.get_data()
    match action:
        case "Завершить":
            api = APIManager()
            await api.make_booking(
                telegram_id=str(message.from_user.id),
                date=data["date"],
                start=data["start"],
                duration=data["duration"],
                end=get_end_time(data["start"], int(data["duration"])),
                instructor_id=data["instructor"],
                bikes=data["bikes"],
                client_phone=data["client_phone"],
            )
            msg: str = read_template("admin/new_booking/done")
            await message.answer(msg, parse_mode="HTML")
            await state.clear()
        case "Выбрать еще байк":
            msg: str = read_template("admin/new_booking/bikes_repeat")
            markup: "ReplyKeyboardMarkup" = get_reply_markup(
                list(data["available_bikes"].keys())
            )
            await message.answer(msg, reply_markup=markup, parse_mode="HTML")
            await state.set_state(NewSideBookingState.bikes)
            return
        case _:
            msg: str = read_template("errors/wrong_action")
            markup: "ReplyKeyboardMarkup" = get_reply_markup(actions)
            await message.answer(msg, reply_markup=markup, parse_mode="HTML")
            await state.set_state(await state.get_state())
            return
