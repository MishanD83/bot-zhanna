from aiogram.fsm.state import State, StatesGroup


TRAFFIC_SOURCE_KEY = "traffic_source"


class OnboardingStates(StatesGroup):
    waiting_name = State()
    waiting_country = State()
    choosing_interests = State()