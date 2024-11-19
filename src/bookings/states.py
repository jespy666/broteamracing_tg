from aiogram.fsm.state import StatesGroup, State


class NewBookingState(StatesGroup):
    """
    States for booking create.
    """
    email = State()
    bikes = State()
    date = State()
    start = State()
    hours = State()
