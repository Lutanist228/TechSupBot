from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
from functions import *
from states import UserStates
from main import bot
from keyboards import *

msg_router = Router()

@msg_router.message(Command("start", ignore_mention=False))
async def main_menu_call(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_message(chat_id=message.from_user.id, text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())

@msg_router.message(UserStates.form_sending)
async def form_send(message: types.Message, state: FSMContext):
    data: dict = await state.get_data()
    chosen_category = data["chosen_category"]
    menu: types.CallbackQuery = data["menu"]
    
    message_text = message.text
    form_topic = chosen_category["Категории"]
    
    # тут осуществляется отправка на почту
    
    await message.delete()
    await menu.edit_text(text=f"""Заявка на тему '{form_topic}' успешно сформирована и отправлена специалисту.\n\nТекст вашего обращения: {message_text}""", reply_markup=User_Keyboards.category(True))
    await state.set_state(UserStates.form_creation)
    
@msg_router.message(Command("create_file", ignore_mention=False))
async def test_file_create(message: types.Message, state: FSMContext):
    create_csv("categories.csv")

@msg_router.message(lambda x: x)
async def spam_delete(message: types.Message):
    await message.delete()