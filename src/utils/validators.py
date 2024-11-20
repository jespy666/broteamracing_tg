from functools import wraps
from datetime import datetime

from typing import (
    Callable,
    Any,
    TYPE_CHECKING,
    Union,
    Dict,
    Optional,
    cast,
    List,
)

from aiogram.types import Message, CallbackQuery
from mypy.reachability import assert_will_always_fail

from src.utils import read_template
from src.utils.keyboards import (
    get_inline_menu,
    get_cancel_button,
    get_reply_markup,
)
from src.api import APIManager

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
    from src.utils import exceptions as exc


def is_valid_date(date: str) -> bool:
    """
    Checking out date has valid format.

    Args:
        date: Date string. Assert format: 'YYYY-MM-DD'.
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_authenticated(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Checking out if user is authenticated in BroTeamRacing.ru.
    """

    @wraps(func)
    async def wrapper(
        event: Union[Message, CallbackQuery],
        state: "FSMContext",
        user: Optional[Dict[str, Union[str, int]]],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        if not user:
            message: Message = (
                event
                if isinstance(event, Message)
                else cast(Message, event.message)
            )
            text: str = read_template("errors/auth.txt")

            buttons = {"Войти": "login"}
            markup: "InlineKeyboardMarkup" = get_inline_menu(buttons)
            await message.answer(text, reply_markup=markup, parse_mode="HTML")
            await state.clear()
        else:
            return await func(event, state, user, *args, **kwargs)

    return wrapper


def date_validator(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Validate user input date (Available and Format).
    """

    @wraps(func)
    async def wrapper(
        message: Message, state: "FSMContext", *args: Any, **kwargs: Any
    ) -> Any:
        date: Optional[str] = message.text
        if is_valid_date(cast(str, date)):
            api = APIManager()
            try:
                slots: Optional[List[str]] = await api.get_available_slots(
                    cast(str, date)
                )
                if not slots:
                    markup: "InlineKeyboardMarkup" = get_cancel_button()
                    busy_text: str = read_template(
                        "errors/busy.txt", date=cast(str, date)
                    )
                    await message.answer(
                        busy_text, reply_markup=markup, parse_mode="HTML"
                    )
                else:
                    await state.update_data(slots=slots, date=date)
                    return await func(message, state, *args, **kwargs)
            except exc.APIConnectionError:
                conn_text: str = read_template("errors/connect.txt")
                await message.answer(conn_text, parse_mode="HTML")
                await state.clear()

    return wrapper


def time_validator(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Validate user time input.
    """

    @wraps(func)
    async def wrapper(
        message: Message, state: "FSMContext", *args: Any, **kwargs: Any
    ) -> Any:
        time: Optional[str] = message.text
        context: Dict[str, Any] = await state.get_data()
        if time in context["starts"]:
            await state.update_data(time=time)
            return await func(message, state, *args, **kwargs)
        else:
            wrong_time_text: str = read_template("errors/wrong_time.txt")
            markup: "ReplyKeyboardMarkup" = get_reply_markup(context["starts"])
            await message.answer(
                wrong_time_text, reply_markup=markup, parse_mode="HTML"
            )

    return wrapper


def hours_validator(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Validate user hours input.
    """

    @wraps(func)
    async def wrapper(
        message: Message, state: "FSMContext", *args: Any, **kwargs: Any
    ) -> Any:
        hour: Optional[str] = message.text
        context: Dict[str, Any] = await state.get_data()
        if hour in context["hours"]:
            await state.update_data(hours=hour)
            return await func(message, state, *args, **kwargs)
        else:
            wrong_hours_text: str = read_template("errors/wrong_hours.txt")
            markup: "ReplyKeyboardMarkup" = get_reply_markup(context["hours"])
            await message.answer(
                wrong_hours_text, reply_markup=markup, parse_mode="HTML"
            )

    return wrapper
