from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from states import UserStates
from objects import *
from keyboards import *
from functions import *

cb_router = Router()

@cb_router.callback_query(UserStates.form_creation)
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
                message = await callback.message.answer(text="""Надеемся, что проблема решена. Если проблема повторится, просим Вас повторно заполнить заявку.\n\nДля возврата в главное меню нажмите на кнопку 'Назад в главное меню' или дождитесь удаления данного сообщения.""")
                await message_delition(message)
                try:
                    await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
                    await state.clear()
                except TelegramBadRequest:
                    pass
            case "unsolved": 
                menu = await callback.message.edit_text(text=f"""Тема Вашего обращения: {chosen_category["Категории"]}\n\nСформируйте текстовое обращение по указанной Вами проблеме и отправьте его в чат с ботом""")
                await state.update_data(menu=menu)
                await state.set_state(UserStates.form_sending)

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
                
@cb_router.callback_query()
async def define_processes(callback: types.CallbackQuery, state: FSMContext):
    process = callback.data
    data: dict = await state.get_data()

    match process:
        case "create_form":
            await state.set_state(UserStates.form_creation)
            await callback.message.edit_text(text="Выберете категорию заявки", reply_markup=await User_Keyboards.categories(state))
         