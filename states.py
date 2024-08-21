from aiogram.fsm.state import State, StatesGroup

class FormActions(StatesGroup):
    form_creation = State()
    text_sending = State()
    text_resending = State()
    mail_resending = State()
    mail_sending = State()
    fio_sending = State()
    fio_resending = State()
    program_sending = State()
    program_resending = State()
    group_sending = State()
    group_resending = State()
    form_claiming = State()
    category_choosing = State()

class FaqActions(StatesGroup):
    surfing_faq = State()
