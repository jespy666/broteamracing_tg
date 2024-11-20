from typing import TYPE_CHECKING, Union, Dict, cast, Any, List

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from src.utils import validators
from src.utils.keyboards import get_cancel_button, get_reply_markup
from src.utils import read_template, get_start_times, get_hours
from src.bookings.states import NewBookingState

if TYPE_CHECKING:
    from aiogram.types import (
        CallbackQuery,
        InlineKeyboardMarkup,
        ReplyKeyboardMarkup,
    )
    from aiogram.fsm.context import FSMContext


booking_router = Router()


@validators.is_authenticated
@booking_router.message(Command("book"))
@booking_router.callback_query(F.data == "book")
async def ask_date(
    event: Union[Message, "CallbackQuery"],
    state: FSMContext,
    user: Dict[str, Union[str, int]],
) -> None:
    """
    First stage of create booking.
    """
    message: Message = (
        event if isinstance(event, Message) else cast(Message, event.message)
    )
    text: str = read_template("booking_create/date.txt", user=user["str"])
    markup: "InlineKeyboardMarkup" = get_cancel_button()
    await message.answer(text, reply_markup=markup, parse_mode="HTML")
    await state.set_state(NewBookingState.date)


@validators.date_validator
@booking_router.message(NewBookingState.date)
async def ask_time(message: Message, state: "FSMContext") -> None:
    """
    Second stage of create booking
    """
    context: Dict[str, Any] = await state.get_data()
    text: str = read_template(
        "booking_create/time.txt",
        date=context["date"],
        slots=context["slots"],
    )

    starts: List[str] = get_start_times(context["slots"])
    markup: "ReplyKeyboardMarkup" = get_reply_markup(starts)
    await message.answer(text, reply_markup=markup, parse_mode="HTML")
    await state.update_data(starts=starts)
    await state.set_state(NewBookingState.time)


@validators.time_validator
@booking_router.message(NewBookingState.time)
async def ask_hours(message: Message, state: "FSMContext") -> None:
    """
    Third stage of create booking
    """
    context: Dict[str, Any] = await state.get_data()
    text: str = read_template("booking_create/hours.txt")

    hours: List[int] = get_hours(context["slots"], context["time"])
    markup: "ReplyKeyboardMarkup" = get_reply_markup(hours)
    await message.answer(text, reply_markup=markup, parse_mode="HTML")
    await state.update_data(hours=hours)
    await state.set_state(NewBookingState.hours)


@validators.hours_validator
@booking_router.message(NewBookingState.hours)
async def ask_bikes(message: Message, state: "FSMContext") -> None:
    """
    Fourth stage of create booking.
    """
    context: Dict[str, Any] = await state.get_data()
    bikes: List[str] = context.get("bikes")  # type: ignore
    if not bikes:
        text: str = read_template("booking_create/bikes.txt")
    else:
        text: str = read_template(  # type: ignore
            "booking_create/bikes_repeat.txt",
            bikes=bikes,
        )
