from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
import asyncio as asy
import subprocess

from states import *
from objects import *
from keyboards import *
from functions import *


cb_router = Router()

@cb_router.callback_query(FormActions.category_choosing)
async def form_creation(callback: types.CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    
    try:
        category_table = data["category_table"] 
        chosen_category = data["chosen_category"]
    except KeyError: pass
    
    if callback.data == "main_menu":
        await state.clear()
        await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
    elif callback.data == "create_form":
        await callback.message.edit_text(text="Выберете категорию заявки", reply_markup=await User_Keyboards.categories(state))
    elif "cat_state" in callback.data:
        category_state = callback.data.split("=")[1]
        
        match category_state:
            case "solved": 
                try:
                    await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
                    await state.clear()
                except TelegramBadRequest:
                    pass
                message = await callback.message.answer(text="""Надеемся, что проблема решена. Если проблема повторится, просим Вас повторно заполнить заявку.""")
                await message_delition(message)
            case "unsolved": 
                menu = await callback.message.edit_text(text=f"""Тема Вашего обращения: {chosen_category["Категории"]}\n\nСформируйте текстовое обращение по указанной Вами проблеме и отправьте его в чат с ботом""")
                await state.update_data(menu=menu)
                await state.set_state(FormActions.text_sending)
    else:
        category_id = int(callback.data.split("=")[1])

        match category_id:
            case 1: 
                await state.update_data(chosen_category=category_table[category_id - 1])
                await callback.message.edit_text(text="""Проверьте, пожалуйста, регистр и язык ввода логина и пароля. Требуется ли консультация специалиста или проблема решена?""", reply_markup=User_Keyboards.category())
            case 2: pass
            case 3: pass
            case 4: pass
            case 5: pass
                
@cb_router.callback_query(FormActions.form_claiming)
async def form_claiming(callback: types.CallbackQuery, state: FSMContext):
    from DataStorage import DataStorage

    
    data: dict = await state.get_data()
    mail_sender = DataStorage.temp_data
    
    try:
        category_table = data["category_table"] 
        chosen_category = data["chosen_category"]
        form_topic = chosen_category["Категории"]
    except KeyError: pass
    
    if callback.data == "send_form":
        # тут осуществляется отправка на почту
        mail_sender.subject = form_topic
        mail_sender.letter_text = f"""ID: {callback.from_user.id}\nОт: {data["printed_mail"]}\nСодержание: {data["printed_text"]}"""
        
        await mail_sender.create_message()
        await mail_sender.send_email()
        
        await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
        message = await callback.message.answer("Заявка успешно сформирована")
        await message_delition(message)
        await state.clear()
    elif callback.data == "content_edit":
        await callback.message.edit_text(text=f"""Тема Вашего обращения: {chosen_category["Категории"]}\n\nСформируйте текстовое обращение по указанной Вами проблеме и отправьте его в чат с ботом""")        
        await state.set_state(FormActions.text_resending)
    elif callback.data == "mail_edit":
        await callback.message.edit_text(text=f"""Укажите электронную почту, на которую будет отправлен ответ специалиста.\n\nУбедительная просьба отправлять почту с указание  специального символа - '@'!""")
        await state.set_state(FormActions.mail_resending)
    elif callback.data == "main_menu":
        await state.clear()
        await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
    elif callback.data == "send_form":
        await state.set_state(FormActions.category_choosing)
        await callback.message.edit_text(text="Выберете категорию заявки", reply_markup=await User_Keyboards.categories(state))

@cb_router.callback_query()
async def define_processes(callback: types.CallbackQuery, state: FSMContext):
    process = callback.data
    data: dict = await state.get_data()

    match process:
        case "create_form":
            await state.set_state(FormActions.category_choosing)
            await callback.message.edit_text(text="Выберете категорию заявки", reply_markup=await User_Keyboards.categories(state))
         