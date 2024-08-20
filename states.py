from aiogram.fsm.state import State, StatesGroup

class FormActions(StatesGroup):
    form_creation = State()
    text_sending = State()
    text_resending = State()
    mail_resending = State()
    mail_sending = State()
    form_claiming = State()
    category_choosing = State()

class FaqActions(StatesGroup):
    surfing_faq = State()
