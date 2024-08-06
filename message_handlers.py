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
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    await state.update_data(printed_text=message.text)
    menu = await menu.edit_text(text=f"""Укажите электронную почту, на которую будет отправлен ответ специалиста.\n\nУбедительная просьба отправлять почту с указание  специального символа - '@'!""")
    await state.update_data(menu=menu)    
    await state.set_state(FormActions.mail_sending)
    await message.delete()

@msg_router.message(FormActions.text_resending)
async def form_claim(message: types.Message, state: FSMContext):
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    chosen_category = data["chosen_category"]
    printed_mail = data["printed_mail"]
    printed_text = message.text
    form_topic = chosen_category["Категории"]
        
    await state.update_data(printed_text=printed_text)
        
    await message.delete()
    await menu.edit_text(text=f"""Проверьте, пожалуйста, введенные Вами данные.\n\nТема обращения: {form_topic}\n\nСодержание обращения: {printed_text}\n\nПочта отправителя: {printed_mail}""", reply_markup=User_Keyboards.category(True))
    await state.set_state(FormActions.form_claiming)
    
@msg_router.message(FormActions.mail_resending)
async def form_claim(message: types.Message, state: FSMContext):
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

@msg_router.message(FormActions.mail_sending)
async def form_claim(message: types.Message, state: FSMContext):
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
    
@msg_router.message(Command("create_file", ignore_mention=False))
async def test_file_create(message: types.Message, state: FSMContext):
    create_csv("categories.csv")

@msg_router.message(lambda x: x)
async def spam_delete(message: types.Message):
    await message.delete()