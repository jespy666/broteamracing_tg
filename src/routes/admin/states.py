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
