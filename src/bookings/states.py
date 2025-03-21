from aiogram.fsm.state import StatesGroup, State


class NewBookingState(StatesGroup):
    """
    Состояния для записи на прокат.
    """

    date = State()
    start = State()
    duration = State()
    instructor = State()
    bike = State()
    amount = State()
    confirm = State()


class CancelBookingState(StatesGroup):
    """
    Состояние для отмены записи на прокат.
    """

    confirm_booking_id = State()
