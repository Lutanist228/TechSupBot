from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
from states import UserStates
from objects import *
from keyboards import *

cb_router = Router()

@cb_router.callback_query()
async def define_processes(callback: types.CallbackQuery, state: FSMContext):
    process = callback.data

    match process:
        case "create_form":
            await state.set_state(UserStates.form_creation)
            await callback.message.edit_text(text="Выберете категорию заявки", reply_markup=User_Keyboards.categories())
         