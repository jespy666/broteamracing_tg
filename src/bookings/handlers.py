from typing import TYPE_CHECKING, TypeVar, Union, Dict, Any, List

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.utils import read_template
from src.keyboards import get_inline_menu, get_cancel_button, get_reply_markup
from src.bookings.states import NewBookingState
from src.middlewares import AccessMiddleware
from src.bookings import utils
from src.api.manager import APIManager

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


booking_router = Router()
booking_router.message.middleware(AccessMiddleware())

E = TypeVar("E", bound=Union[Message, CallbackQuery])


@booking_router.message(Command("book"))
@booking_router.callback_query(F.data == "book")
async def start_booking(
    event: E,
    state: "FSMContext",
    has_access: bool,
) -> None:
    """
    Состояние 1. Начало записи. Запрос Даты.
    """
    message = event if isinstance(event, Message) else event.message
    if not has_access:
        msg = read_template("errors/access")
        markup: "InlineKeyboardMarkup" = get_inline_menu(
            {"Привязать аккаунт": "link-account"}
        )
    else:
        markup: "InlineKeyboardMarkup" = get_cancel_button()
        msg = read_template("booking_create/date")

    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.set_state(NewBookingState.date)


@booking_router.message(NewBookingState.date)
async def ask_start(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Запрос времени начала.
    """
    date: str = message.text
    if not utils.validate_date(date):
        msg: str = read_template("errors/incorrect_date")
        markup: "InlineKeyboardMarkup" = get_cancel_button()
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())

    api = APIManager()
    day_info: List[Dict[str, Any]] = await api.load_day_info(date)
    starts: List[str] = utils.get_start_times(day_info)

    msg = read_template("booking_create/start")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(starts)
    await state.update_data(day_info=day_info, starts=starts)
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.set_state(NewBookingState.start)


@booking_router.message(NewBookingState.start)
async def ask_duration(message: "Message", state: "FSMContext") -> None:
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

    available_hours: List[int] = utils.get_available_time_range(
        data["starts"],
        start,
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(available_hours)
    msg = read_template("booking_create/duration")
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(durations=available_hours)
    await state.set_state(NewBookingState.duration)
