from aiogram.fsm.state import StatesGroup, State


class NewSideBookingState(StatesGroup):
    """
    Состояния для создания стороннего проката.
    """

    date = State()
    start = State()
    duration = State()
    instructor = State()
    client_phone = State()
    bikes = State()
    amount = State()
    confirm = State()


class AcceptBookingAdminState(StatesGroup):
    """
    Состояния для принятия проката администратором.
    """

    booking_id = State()
    instructor = State()
    bike = State()


class CancelBookingAdminState(StatesGroup):
    """
    Состояния для отмены проката администратором.
    """

    booking_id = State()


class PendingBookingAdminState(StatesGroup):
    """
    Состояния для перевода проката в ожидание администратором.
    """

    booking_id = State()


class AdminChangeInstructorState(StatesGroup):
    """
    Состояния замены инструктора администратором.
    """

    booking_id = State()
    instructor = State()
