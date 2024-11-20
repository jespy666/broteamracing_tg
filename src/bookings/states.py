from aiogram.fsm.state import StatesGroup, State


class NewBookingState(StatesGroup):
    """
    States for booking create.
    """

    date = State()
    time = State()
    hours = State()
    bikes = State()
