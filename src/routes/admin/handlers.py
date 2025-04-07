from typing import Union, TYPE_CHECKING, TypeVar, List, Dict, Any, Optional

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F

from src.routes.admin import states
from src.keyboards import get_inline_menu, get_reply_markup
from src.middlewares import AdminMiddleware
from src import utils as root_utils
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
        msg: str = root_utils.read_template("errors/restricted")
        await message.answer(msg, parse_mode="HTML")
        return

    markup: "InlineKeyboardMarkup" = get_inline_menu(utils.MENU)
    msg: str = root_utils.read_template("admin/main")
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
        msg: str = root_utils.read_template("errors/restricted")
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    msg: str = root_utils.read_template("admin/new_booking/date")
    await message.answer(msg, parse_mode="HTML")
    await state.set_state(states.NewSideBookingState.date)


@admin_router.message(states.NewSideBookingState.date)
async def ask_start(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Запрос времени начала.
    """
    date: str = message.text
    if not root_utils.validate_date(date):
        msg: str = root_utils.read_template("errors/date")
        await message.answer(msg, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    day_info: List[Dict[str, Any]] = await api.load_day_info(date)
    starts: List[str] = root_utils.get_start_times(day_info)

    msg = root_utils.read_template("admin/new_booking/start")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(starts)
    await state.update_data(day_info=day_info, starts=starts, date=date)
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.set_state(states.NewSideBookingState.start)


@admin_router.message(states.NewSideBookingState.start)
async def ask_duration(message: Message, state: "FSMContext") -> None:
    """
    Состояние 3. Запрос длительности проката.
    """
    start: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if start not in data["starts"]:
        msg = root_utils.read_template(
            "errors/chose",
            entity="время начала",
        )
        markup: "ReplyKeyboardMarkup" = get_reply_markup(data["starts"])
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    available_hours: List[int] = root_utils.get_available_time_range(
        data["starts"],
        start,
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(available_hours)
    msg = root_utils.read_template("admin/new_booking/duration")
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(durations=available_hours, start=start)
    await state.set_state(states.NewSideBookingState.duration)


@admin_router.message(states.NewSideBookingState.duration)
async def ask_instructor(message: Message, state: "FSMContext") -> None:
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
    msg = root_utils.read_template("admin/new_booking/instructor")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(list(instructors.keys()))
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(instructors=instructors, duration=int(duration))
    await state.set_state(states.NewSideBookingState.client_phone)


@admin_router.message(states.NewSideBookingState.client_phone)
async def ask_client_phone(message: Message, state: "FSMContext") -> None:
    """
    Состояние 5. Запрос телефона клиента.
    """
    instructor: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if instructor not in list(data["instructors"].keys()):
        msg = root_utils.read_template("errors/chose", entity="инструктора")
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            list(data["instructors"].keys())
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    msg: str = root_utils.read_template("admin/new_booking/phone")
    await state.update_data(instructor=data["instructors"][instructor])
    await message.answer(msg, parse_mode="HTML")
    await state.set_state(states.NewSideBookingState.instructor)


@admin_router.message(states.NewSideBookingState.instructor)
async def ask_bikes(message: Message, state: "FSMContext") -> None:
    """
    Состояние 5. Запрос байков.
    """
    client_phone: str = message.text
    if not utils.validate_phone_number(client_phone):
        msg: str = root_utils.read_template("errors/phone")
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
    msg = root_utils.read_template("admin/new_booking/bikes1")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        list(available_bikes.keys())
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(
        available_bikes=available_bikes,
        client_phone=client_phone,
    )
    await state.set_state(states.NewSideBookingState.bikes)


@admin_router.message(states.NewSideBookingState.bikes)
async def ask_amount(message: Message, state: "FSMContext") -> None:
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

    msg: str = root_utils.read_template("admin/new_booking/amount")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        list(range(1, data["available_bikes"][bike] + 1))
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(bike=bike)
    await state.set_state(states.NewSideBookingState.amount)


@admin_router.message(states.NewSideBookingState.amount)
async def checkout_bikes(message: Message, state: "FSMContext") -> None:
    """
    Состояние 7. Проверка количества байков.
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
            list(range(data["available_bikes"][data["bike"]]))
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
        "admin/new_booking/bikes2",
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
        available_bikes=available_bikes,
        bikes=bikes,
    )
    await state.set_state(states.NewSideBookingState.confirm)


@admin_router.message(states.NewSideBookingState.confirm)
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
                date=data["date"],
                start=data["start"],
                duration=data["duration"],
                end=root_utils.get_end_time(
                    data["start"],
                    int(data["duration"]),
                ),
                instructor_id=data["instructor"],
                bikes=data["bikes"],
                client_phone=data["client_phone"],
            )
            msg: str = root_utils.read_template("admin/new_booking/done")
            await message.answer(msg, parse_mode="HTML")
            await state.clear()
        case "Выбрать еще байк":
            msg: str = root_utils.read_template(
                "admin/new_booking/bikes_repeat"
            )
            markup: "ReplyKeyboardMarkup" = get_reply_markup(
                list(data["available_bikes"].keys())
            )
            await message.answer(msg, reply_markup=markup, parse_mode="HTML")
            await state.set_state(states.NewSideBookingState.bikes)
            return
        case _:
            msg: str = root_utils.read_template(
                "errors/chose", entity="действие"
            )
            markup: "ReplyKeyboardMarkup" = get_reply_markup(actions)
            await message.answer(msg, reply_markup=markup, parse_mode="HTML")
            await state.set_state(await state.get_state())
            return


@admin_router.message(Command("admin_accept"))
@admin_router.callback_query(F.data == "admin_accept")
async def ask_booking_id(
    event: E,
    state: "FSMContext",
    is_admin: bool,
) -> None:
    """
    Состояние 1. Запрос ID проката.
    """
    message = event if isinstance(event, Message) else event.message
    if not is_admin:
        msg: str = root_utils.read_template("errors/restricted")
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    api = APIManager()
    bookings: List[Dict[str, str]] = await api.get_bookings("pending")
    if not bookings:
        msg: str = root_utils.read_template(
            "errors/empty_bookings",
            action="подтверждения",
        )
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return
    msg: str = root_utils.read_template(
        "admin/accept/booking_id",
        bookings=root_utils.render_bookings(bookings),
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        [booking["id"] for booking in bookings]
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(bookings=bookings)
    await state.set_state(states.AcceptBookingAdminState.booking_id)


@admin_router.message(states.AcceptBookingAdminState.booking_id)
async def ask_instructor(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Запрос инструктора для проката.
    """
    booking_id: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not root_utils.validate_booking_id(booking_id, data["bookings"]):
        msg: str = root_utils.read_template(
            "errors/chose",
            entity="ID проката",
        )
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
    instructors: Dict[str, int] = await api.get_available_instructors(
        date=booking["raw_date"],
        start=booking["start"],
        duration=int(booking["duration"]),
    )
    msg: str = root_utils.read_template(
        "admin/accept/instructor",
        instructor=booking["instructor"],
    )
    buttons: List[str] = list(instructors.keys())
    buttons.append("Не менять инструктора")
    markup: "ReplyKeyboardMarkup" = get_reply_markup(buttons)
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(available_instructors=instructors, booking=booking)
    await state.set_state(states.AcceptBookingAdminState.instructor)


@admin_router.message(states.AcceptBookingAdminState.instructor)
async def ask_bike(message: Message, state: "FSMContext") -> None:
    """
    Состояние 3. Запрос байка для инструктора.
    """
    data: Dict[str, Any] = await state.get_data()
    booking: Dict[str, Union[str, int]] = data["booking"]
    instructor: str = (
        message.text
        if not message.text == "Не менять инструктора"
        else booking["instructor"]
    )
    if not message.text == "Не менять инструктора":
        if instructor not in data["available_instructors"].keys():
            msg: str = root_utils.read_template(
                "errors/chose",
                entity="инструктора",
            )
            buttons: List[str] = list(data["available_instructors"].keys())
            buttons.append("Не менять инструктора")
            markup: "ReplyKeyboardMarkup" = get_reply_markup(buttons)
            await message.answer(msg, reply_markup=markup, parse_mode="HTML")
            await state.set_state(await state.get_state())
            return

    msg: str = root_utils.read_template("admin/accept/bike")
    api = APIManager()
    available_bikes: Dict[str, int] = await api.get_available_bikes(
        date=booking["raw_date"],
        start=booking["start"],
        duration=booking["duration"],
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        list(available_bikes.keys())
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(
        instructor=instructor,
        available_bikes=available_bikes,
    )
    await state.set_state(states.AcceptBookingAdminState.bike)


@admin_router.message(states.AcceptBookingAdminState.bike)
async def accept_booking(message: Message, state: "FSMContext") -> None:
    """
    Состояние 4. Подтверждение проката.
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

    instructor_id: int = (
        data["available_instructors"].get(data["instructor"])
        or data["booking"]["instructor_id"]
    )
    api = APIManager()
    error: Optional[str] = await api.accept_booking(
        int(data["booking"]["id"]),
        int(instructor_id),
        bike,
        is_admin=True,
    )
    if error:
        msg: str = root_utils.read_template(
            "admin/accept/error",
            error=error,
        )
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            [booking["id"] for booking in data["bookings"]]
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(states.AcceptBookingAdminState.booking_id)
        return

    msg: str = root_utils.read_template("admin/accept/done")
    await message.answer(msg, parse_mode="HTML")
    await state.clear()


@admin_router.message(Command("admin_cancel"))
@admin_router.callback_query(F.data == "admin_cancel")
async def ask_booking_id(
    event: E,
    state: "FSMContext",
    is_admin: bool,
) -> None:
    """
    Состояние 1. Запрос ID проката.
    """
    message = event if isinstance(event, Message) else event.message
    if not is_admin:
        msg: str = root_utils.read_template("errors/restricted")
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    api = APIManager()
    bookings: List[Dict[str, str]] = await api.get_bookings()
    if not bookings:
        msg: str = root_utils.read_template(
            "errors/empty_bookings",
            action="отмены",
        )
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return
    msg: str = root_utils.read_template(
        "admin/cancel/booking_id",
        bookings=root_utils.render_bookings(bookings),
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        [booking["id"] for booking in bookings]
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(bookings=bookings)
    await state.set_state(states.CancelBookingAdminState.booking_id)


@admin_router.message(states.CancelBookingAdminState.booking_id)
async def cancel_booking(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Отмена записи на прокат.
    """
    booking_id: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not root_utils.validate_booking_id(booking_id, data["bookings"]):
        msg: str = root_utils.read_template(
            "errors/chose",
            entity="ID проката",
        )
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            [booking["id"] for booking in data["bookings"]]
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    await api.cancel_booking(int(booking_id), is_admin=True)
    msg: str = root_utils.read_template("admin/cancel/done")
    await message.answer(msg, parse_mode="HTML")
    await state.clear()


@admin_router.message(Command("admin_pending"))
@admin_router.callback_query(F.data == "admin_pending")
async def ask_booking_id(
    event: E,
    state: "FSMContext",
    is_admin: bool,
) -> None:
    """
    Состояние 1. Запрос ID проката.
    """
    message = event if isinstance(event, Message) else event.message
    if not is_admin:
        msg: str = root_utils.read_template("errors/restricted")
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    api = APIManager()
    bookings: List[Dict[str, str]] = await api.get_bookings("confirmed")
    if not bookings:
        msg: str = root_utils.read_template(
            "errors/empty_bookings",
            action="перевода в ожидание",
        )
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return
    msg: str = root_utils.read_template(
        "admin/pending/booking_id",
        bookings=root_utils.render_bookings(bookings),
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        [booking["id"] for booking in bookings]
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(bookings=bookings)
    await state.set_state(states.PendingBookingAdminState.booking_id)


@admin_router.message(states.PendingBookingAdminState.booking_id)
async def pending_booking(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Перевод проката в ожидание.
    """
    booking_id: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not root_utils.validate_booking_id(booking_id, data["bookings"]):
        msg: str = root_utils.read_template(
            "errors/chose",
            entity="ID проката",
        )
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            [booking["id"] for booking in data["bookings"]]
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    await api.pending_booking(int(booking_id))
    msg: str = root_utils.read_template("admin/pending/done")
    await message.answer(msg, parse_mode="HTML")
    await state.clear()


@admin_router.message(Command("admin_change_instructor"))
@admin_router.callback_query(F.data == "admin_change_instructor")
async def ask_booking_id(
    event: E,
    state: "FSMContext",
    is_admin: bool,
) -> None:
    """
    Состояние 1. Запрос ID проката.
    """
    message = event if isinstance(event, Message) else event.message
    if not is_admin:
        msg: str = root_utils.read_template("errors/restricted")
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    api = APIManager()
    bookings: List[Dict[str, str]] = await api.get_bookings()
    if not bookings:
        msg: str = root_utils.read_template(
            "errors/empty_bookings",
            action="замены инструктора",
        )
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return
    msg: str = root_utils.read_template(
        "admin/pending/booking_id",
        bookings=root_utils.render_bookings(bookings),
    )
    markup: "ReplyKeyboardMarkup" = get_reply_markup(
        [booking["id"] for booking in bookings]
    )
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(bookings=bookings)
    await state.set_state(states.AdminChangeInstructorState.booking_id)


@admin_router.message(states.AdminChangeInstructorState.booking_id)
async def ask_instructor(message: Message, state: "FSMContext") -> None:
    """
    Состояние 2. Запрос нового инструктора.
    """
    booking_id: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if not root_utils.validate_booking_id(booking_id, data["bookings"]):
        msg: str = root_utils.read_template(
            "errors/chose",
            entity="ID проката",
        )
        markup: "ReplyKeyboardMarkup" = get_reply_markup(
            [booking["id"] for booking in data["bookings"]]
        )
        await message.answer(msg, reply_markup=markup, parse_mode="HTML")
        await state.set_state(await state.get_state())
        return

    api = APIManager()
    booking: Dict[str, Union[str, int]] = [
        b for b in data["bookings"] if b["id"] == int(booking_id)
    ][0]
    instructors: Dict[str, int] = await api.get_available_instructors(
        booking["raw_date"],
        booking["start"],
        int(booking["duration"]),
    )
    if not instructors:
        msg: str = root_utils.read_template(
            "admin/change_instructor/instructor_none",
        )
        await message.answer(msg, parse_mode="HTML")
        await state.clear()
        return

    markup: "ReplyKeyboardMarkup" = get_reply_markup(list(instructors.keys()))
    msg: str = root_utils.read_template("admin/change_instructor/instructor")
    await message.answer(msg, reply_markup=markup, parse_mode="HTML")
    await state.update_data(instructors=instructors, booking_id=booking_id)
    await state.set_state(states.AdminChangeInstructorState.instructor)


@admin_router.message(states.AdminChangeInstructorState.instructor)
async def change_instructor(message: Message, state: "FSMContext") -> None:
    """
    Состояние 3. Замена инструктора на прокате.
    """
    instructor: str = message.text
    data: Dict[str, Any] = await state.get_data()
    if instructor not in data["instructors"].keys():
        msg: str = root_utils.read_template(
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
    await api.change_instructor(
        int(data["booking_id"]),
        int(data["instructors"][instructor]),
    )
    msg: str = root_utils.read_template("admin/change_instructor/done")
    await message.answer(msg, parse_mode="HTML")
    await state.clear()
