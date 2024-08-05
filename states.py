from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    authorization = State()
    form_creation = State()


