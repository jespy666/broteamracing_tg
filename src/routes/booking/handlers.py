from typing import TYPE_CHECKING, TypeVar, Union, Dict, Any, List, Optional

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from src.keyboards import get_cancel_button, get_reply_markup
from src.routes.booking.states import NewBookingState, CancelBookingState
from src.middlewares import AuthMiddleware
from src.routes.booking import utils
from src.api.manager import APIManager
from src import utils as root_utils

from config import settings

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


booking_router = Router()
booking_router.message.middleware(AuthMiddleware())
booking_router.callback_query.middleware(AuthMiddleware())

E = TypeVar("E", bound=Union[Message, CallbackQuery])


@booking_router.message(Command("booking"))
@booking_router.callback_query(F.data == "booking")
async def start_booking(
    event: E,
    state: "FSMContext",
    is_authenticated: bool,
) -> None:
    """
    Состояние 1. Начало записи. Запрос Даты.
    """
    message = event if isinstance(event, Message) else event.message
    if not is_authenticated:
        msg = root_utils.read_template(
            "connect",
            link=f"{settings.BASE_API_URL}/my/connect_tg_account/",
        )
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    markup: "InlineKeyboardMarkup" = get_cancel_button()
    msg = root_utils.read_template("booking_create/date")
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.set_state(NewBookingState.date)


@booking_router.message(NewBookingState.date)
async def ask_start(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Запрос времени начала.
    """
    date: str = message.text
    if not root_utils.validate_date(date):
        msg: str = root_utils.read_template("errors/date")
        markup: "InlineKeyboardMarkup" = get_cancel_button()
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    day_info: List[Dict[str, Any]] = await api.load_day_info(date)
    starts: List[str] = root_utils.get_start_times(day_info)

    msg = root_utils.read_template("booking_create/start")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(starts)
    await state.update_data(day_info=day_info, starts=starts, date=date)
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.set_state(NewBookingState.start)


@booking_router.message(NewBookingState.start)
async def ask_duration(message: "Message", state: "FSMContext") -> None:
    """
    Состояние 3. Запрос длительности проката.
    """
    start: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if start not in data["starts"]:
        msg = root_utils.read_template("errors/chose", entity="время начала")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(data["starts"])
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    available_hours: List[int] = root_utils.get_available_time_range(
        data["starts"],
        start,
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(available_hours)
    msg = root_utils.read_template("booking_create/duration")
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(durations=available_hours, start=start)
    await state.set_state(NewBookingState.duration)


@booking_router.message(NewBookingState.duration)
async def ask_instructor(message: "Message", state: "FSMContext") -> None:
    """
    Состояние 4. Запрос инструктора.
    """
    duration: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not root_utils.validate_duration(duration, data["durations"]):
        msg = root_utils.read_template(
            "errors/chose",
            entity="длительность",
        )
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
    msg = root_utils.read_template("booking_create/instructor")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(list(instructors.keys()))
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(instructors=instructors, duration=int(duration))
    await state.set_state(NewBookingState.instructor)


@booking_router.message(NewBookingState.instructor)
async def ask_bikes(message: "Message", state: "FSMContext") -> None:
    """
    Состояние 5. Запрос байков.
    """
    instructor: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if instructor not in list(data["instructors"].keys()):
        msg = root_utils.read_template(
            "errors/chose",
            entity="инструктора",
        )
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(data["instructors"].keys())
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    available_bikes: Dict[str, int] = await api.get_available_bikes(
        data["date"],
        data["start"],
        data["duration"],
    )
    msg = root_utils.read_template("booking_create/bikes1")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        list(available_bikes.keys())
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(
        available_bikes=available_bikes,
        instructor=data["instructors"][instructor],
    )
    await state.set_state(NewBookingState.bike)


@booking_router.message(NewBookingState.bike)
async def ask_amount(message: "Message", state: "FSMContext") -> None:
    """
    Состояние 6. Запрос количества байков.
    """
    bike: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if bike not in data["available_bikes"].keys():
        msg: str = root_utils.read_template("errors/chose", entity="байк")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(data["available_bikes"].keys())
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    msg: str = root_utils.read_template("booking_create/amount")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        list(range(1, data["available_bikes"][bike] + 1))
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(bike=bike)
    await state.set_state(NewBookingState.amount)


@booking_router.message(NewBookingState.amount)
async def checkout_bikes(message: "Message", state: "FSMContext") -> None:
    """
    Состояние 7. Проверка количества.
    """
    amount: str = message.text
    data: Dict[str, Any] = await state.get_data()
    available_bikes: Dict[str, int] = data["available_bikes"]
    bike: str = data["bike"]
    if not root_utils.validate_amount(amount, available_bikes[bike]):
        msg: str = root_utils.read_template(
            "errors/chose",
            entity="количество",
        )
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(range(1, data["available_bikes"][data["bike"]] + 1))
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    # Обновляем выбранные байки
    bikes: Optional[Dict[str, int]] = data.get("bikes", {})
    bikes[bike] = int(amount)

    reduced_bikes: Union[Dict[str, int], False] = root_utils.reduce_bike_count(
        (bike, int(amount)),
        available_bikes,
    )
    if reduced_bikes is False:
        msg: str = root_utils.read_template("errors/overbike")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(range(1, data["available_bikes"][data["bike"]] + 1))
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    msg: str = root_utils.read_template(
        "booking_create/bikes2",
        bikes=root_utils.render_chosen_bikes(bikes),
    )
    kb: List[str] = ["Завершить"]

    # Проверка на доступность байков
    if len(reduced_bikes) == 1:
        # Если остался только один байк, резервируем его для инструктора
        key, value = next(iter(available_bikes.items()))
        if value > 1:
            kb.append("Выбрать еще байк")
    else:
        kb.append("Выбрать еще байк")

    markup: "ReplyKeyboardMarkup" = get_reply_markup(kb)

    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(
        bike=None,
        available_bikes=reduced_bikes,
        bikes=bikes,
    )
    await state.set_state(NewBookingState.confirm)


@booking_router.message(NewBookingState.confirm)
async def confirm(message: "Message", state: "FSMContext") -> None:
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
                end=root_utils.get_end_time(
                    data["start"],
                    int(data["duration"]),
                ),
                instructor_id=data["instructor"],
                bikes=data["bikes"],
            )
            msg: str = root_utils.read_template("booking_create/done")
            await message.answer(msg, parse_mode="HTML")
            await state.clear()
        case "Выбрать еще байк":
            msg: str = root_utils.read_template("booking_create/bikes_repeat")
            markup: "ReplyKeyboardMarkup" = get_reply_markup(
                list(data["available_bikes"].keys())
            )
            await message.answer(msg, reply_markup=markup, parse_mode="HTML")
            await state.set_state(NewBookingState.bike)
            return
        case _:
            msg: str = root_utils.read_template(
                "errors/chose",
                entity="действие",
            )
            markup: "ReplyKeyboardMarkup" = get_reply_markup(actions)
            await message.answer(msg, reply_markup=markup, parse_mode="HTML")
            await state.set_state(await state.get_state())
            return


@booking_router.message(Command("cancel"))
@booking_router.callback_query(F.data == "cancel")
async def ask_booking_id(
    event: E,
    state: "FSMContext",
    is_authenticated: bool,
) -> None:
    """
    Состояние 1. Отмена записи. Показ всех предстоящих записей.
    """
    message = event if isinstance(event, Message) else event.message
    if not is_authenticated:
        msg = root_utils.read_template(
            "connect",
            link=f"{settings.BASE_API_URL}/my/connect_tg_account/",
        )
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return
    else:
        api = APIManager()
        bookings: List[Dict[str, Union[str, int]]] = (
            await api.get_user_active_bookings(str(event.from_user.id))
        )

        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            [booking["id"] for booking in bookings]
        )
        msg = root_utils.read_template(
            "booking_cancel/list",
            bookings=utils.render_bookings(bookings),
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.update_data(bookings=bookings)
        await state.set_state(CancelBookingState.confirm_booking_id)


@booking_router.message(CancelBookingState.confirm_booking_id)
async def cancel_booking(message: "Message", state: "FSMContext") -> None:
    """
    Состояние 2. Проверка ID записи и ее отмена.
    """
    booking_id: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not root_utils.validate_booking_id(booking_id, data["bookings"]):
        msg: str = root_utils.read_template(
            "errors/chose",
            entity="ID записи",
        )
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            [booking["id"] for booking in data["bookings"]]
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    await api.cancel_booking(int(booking_id))
    msg: str = root_utils.read_template("booking_cancel/done")
    await message.answer(msg, parse_mode="HTML")
    await state.clear()
