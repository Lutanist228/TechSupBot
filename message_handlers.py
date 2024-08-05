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

@msg_router.message(Command("create_file", ignore_mention=False))
async def test_file_create(message: types.Message, state: FSMContext):
    create_csv("categories.csv")

@msg_router.message(lambda x: x)
async def spam_delete(message: types.Message):
    await message.delete()