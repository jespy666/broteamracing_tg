from aiogram.fsm.state import StatesGroup, State


class AcceptBookingState(StatesGroup):
    """
    Состояния для взятия в работу проката.
    """

    booking = State()
    bike = State()


class DeclineBookingState(StatesGroup):
    """
    Состояние для отказа от проката персонала.
    """

    booking = State()
