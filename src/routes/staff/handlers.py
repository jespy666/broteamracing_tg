from typing import TYPE_CHECKING, TypeVar, Union, Dict, List, Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.api.manager import APIManager
from src.routes.staff import utils
from src.routes.booking.utils import validate_booking_id
from src.middlewares import StaffMiddleware
from src.utils import read_template
from src.keyboards import get_inline_menu, get_reply_markup
from src.routes.staff.states import AcceptBookingState

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
    from aiogram.fsm.context import FSMContext


staff_router = Router()
staff_router.message.middleware(StaffMiddleware())
staff_router.callback_query.middleware(StaffMiddleware())

E = TypeVar("E", bound=Union[Message, CallbackQuery])


@staff_router.message(Command("staff"))
async def staff_menu(
    message: "Message",
    instructor_id: Union[int, bool],
) -> None:
    """
    Меню для персонала.
    """
    if not instructor_id:
        msg: str = read_template("staff/restricted")
        await message.answer(msg, parse_mode="HTML")
        return

    markup: "InlineKeyboardMarkup" = get_inline_menu(utils.MENU)
    msg: str = read_template("staff/main")
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")


@staff_router.message(Command("staff_accept"))
@staff_router.callback_query(F.data == "staff_accept")
async def ask_booking_id(
    event: E,
    state: "FSMContext",
    instructor_id: Union[int, bool],
) -> None:
    """
    Состояние 1. Список прокатов. Запрос ID.
    """
    message = event if isinstance(event, Message) else event.message
    if not instructor_id:
        msg: str = read_template("staff/restricted")
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    api = APIManager()
    bookings: List[Dict[str, str]] = await api.get_bookings_to_accept()
    msg = read_template(
        "staff/accept/booking_id",
        bookings=utils.render_bookings_to_accept(bookings),
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        [booking["id"] for booking in bookings]
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(bookings=bookings, instructor_id=instructor_id)
    await state.set_state(AcceptBookingState.booking)


@staff_router.message(AcceptBookingState.booking)
async def ask_bike(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Запрос байка для инструктора.
    """
    booking_id: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not validate_booking_id(booking_id, data["bookings"]):
        msg: str = read_template("staff/accept/wrong_booking_id")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            [booking["id"] for booking in data["bookings"]]
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    booking: Dict[str, Union[str, int]] = [
        b for b in data["bookings"] if b["id"] == int(booking_id)
    ][0]
    api = APIManager()
    available_bikes: Dict[str, int] = await api.get_available_bikes(
        date=booking["raw_date"],
        start=booking["start"],
        duration=int(booking["duration"]),
    )
    msg: str = read_template("staff/accept/bike")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        list(available_bikes.keys())
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(available_bikes=available_bikes, booking=booking)
    await state.set_state(AcceptBookingState.bike)


@staff_router.message(AcceptBookingState.bike)
async def accept_booking(message: Message, state: "FSMContext") -> None:
    """
    Состояние 3. Взятие в работу проката.
    """
    bike: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if bike not in data["available_bikes"].keys():
        msg: str = read_template("staff/accept/wrong_bike")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(data["available_bikes"].keys())
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    await api.accept_booking(
        int(data["booking"]["id"]),
        data["instructor_id"],
        data["available_bikes"][bike],
    )
    msg: str = read_template("staff/accept/done")
    await message.answer(msg, parse_mode="HTML")
    await state.clear()
