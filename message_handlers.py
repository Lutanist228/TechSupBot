from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
from functions import *
from states import *
from main import bot
from keyboards import *

msg_router = Router()

@msg_router.message(Command("start", ignore_mention=False))
async def main_menu_call(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_message(chat_id=message.from_user.id, text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
    
@msg_router.message(FormActions.text_sending)
async def text_capture(message: types.Message, state: FSMContext):
    from DataStorage import DataStorage
    await state.update_data(printed_text=message.text)
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
        
    if data["chosen_category"] != "Обратная связь":
        menu = await menu.edit_text(text=f"""Укажите электронную почту, на которую будет отправлен ответ специалиста.\n\nУбедительная просьба отправлять почту с указанием специального символа - '@'!""")
        await state.update_data(menu=menu)    
        await state.set_state(FormActions.mail_sending)
        await message.delete()
    else:
        mail_sender = DataStorage.temp_data
        
        mail_sender.subject = data["chosen_category"]
        mail_sender.letter_text = f"""ID пользователя: {message.from_user.id}\n\nСодержание: {data["printed_text"]}"""
        
        await mail_sender.create_message()
        await mail_sender.send_email(state, message)
        await menu.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
        bot_message = await message.answer("Обратная связь успешно отправлена!")
        await message.delete()
        await message_delition(bot_message)
        await state.clear()

@msg_router.message(FormActions.text_resending)
async def text_recapture(message: types.Message, state: FSMContext):
    data: dict = await state.get_data()
    try:
        menu: types.CallbackQuery = data["menu"]
    except KeyError: pass
    chosen_category = data["chosen_category"]
    printed_mail = data["printed_mail"]
    printed_text = message.text
    form_topic = chosen_category["Категории"]
        
    await state.update_data(printed_text=printed_text)
        
    await message.delete()
    await menu.edit_text(text=f"""Проверьте, пожалуйста, введенные Вами данные.\n\nТема обращения: {form_topic}\n\nСодержание обращения: {printed_text}\n\nПочта отправителя: {printed_mail}""", reply_markup=User_Keyboards.category(True))
    await state.set_state(FormActions.form_claiming)
    
@msg_router.message(FormActions.mail_resending, F.text.contains("@"))
async def mail_recapture(message: types.Message, state: FSMContext):
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    chosen_category = data["chosen_category"]
    printed_mail = message.text
    printed_text = data["printed_text"]
    form_topic = chosen_category["Категории"]
        
    await state.update_data(printed_mail=printed_mail)
        
    await message.delete()
    await menu.edit_text(text=f"""Проверьте, пожалуйста, введенные Вами данные.\n\nТема обращения: {form_topic}\n\nСодержание обращения: {printed_text}\n\nПочта отправителя: {printed_mail}""", reply_markup=User_Keyboards.category(True))
    await state.set_state(FormActions.form_claiming)

@msg_router.message(FormActions.mail_sending, F.text.contains("@"))
async def mail_capture(message: types.Message, state: FSMContext):
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    chosen_category = data["chosen_category"]
    printed_mail = message.text
    printed_text = data["printed_text"]
    form_topic = chosen_category["Категории"]
    
    await state.update_data(printed_mail=printed_mail)
        
    await message.delete()
    await menu.edit_text(text=f"""Проверьте, пожалуйста, введенные Вами данные.\n\nТема обращения: {form_topic}\n\nСодержание обращения: {printed_text}\n\nПочта отправителя: {printed_mail}""", reply_markup=User_Keyboards.category(True))
    await state.set_state(FormActions.form_claiming)
        
@msg_router.message(lambda x: x)
async def spam_delete(message: types.Message):
    await message.delete()