from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder 
from aiogram.exceptions import TelegramBadRequest
from aiogram.types.input_media_photo import InputMediaPhoto

from functions import *
from states import *
from main import bot
from keyboards import *

msg_router = Router()

@msg_router.message(Command("start", ignore_mention=False))
async def main_menu_call(message: types.Message, state: FSMContext):
    from DataStorage import DataStorage
    data = await state.get_data()
    DataStorage.erase_objects(message.from_user.id)
    
    try:
        [await elem.delete() for elem in data["media_group_msg"]]
    except KeyError: pass
    await state.clear()
    
    await bot.send_message(chat_id=message.from_user.id, text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
    
@msg_router.message(FormActions.text_sending)
async def text_capture(message: types.Message, state: FSMContext):
    from DataStorage import DataStorage
    
    await state.update_data(printed_text=message.text)
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
        
    if data["chosen_category"] != "Обратная связь":
        menu = await menu.edit_text(text=f"Укажите Ваше ФИО. Просим отправить ФИО одним сообщением")
        await state.update_data(menu=menu)
        await state.set_state(FormActions.fio_sending)
        await message.delete()
    else:
        mail_sender = DataStorage.objects.get("mail_sender_obj")
        
        mail_sender.subject = data["chosen_category"]
        mail_sender.letter_text = f"""ID пользователя: {message.from_user.id}\n\nСодержание: {data["printed_text"]}"""
        
        await mail_sender.create_message(state, message)
        await mail_sender.send_email(state, message)
        await menu.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
        bot_message = await message.answer("Обратная связь успешно отправлена!")
        await message.delete()
        await message_delition(bot_message)
        await state.clear()

@msg_router.message(FormActions.text_resending)
async def text_recapture(message: types.Message, state: FSMContext):
    await state.update_data(printed_text=message.text)
    data: dict = await state.get_data()
    try:
        menu: types.CallbackQuery = data["menu"]
    except KeyError: pass
    
    await form_displaying(data=data, menu=menu, state=state, message=message)
    
@msg_router.message(FormActions.fio_sending)
async def fio_capture(message: types.Message, state: FSMContext):
    await state.update_data(user_fio=message.text)
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    
    menu = await menu.edit_text(text=f"Укажите наименование Вашей программы обучения")
    await state.update_data(menu=menu)
    await state.set_state(FormActions.program_sending)
    await message.delete()
    
@msg_router.message(FormActions.fio_resending)
async def fio_recapture(message: types.Message, state: FSMContext):
    await state.update_data(user_fio=message.text)
    data: dict = await state.get_data()
    try:
        menu: types.CallbackQuery = data["menu"]
    except KeyError: pass
    
    await form_displaying(data=data, menu=menu, state=state, message=message)
    
@msg_router.message(FormActions.program_sending)
async def program_capture(message: types.Message, state: FSMContext):
    await state.update_data(user_program=message.text)
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    
    menu = await menu.edit_text(text=f"Укажите Вашу группу, если знаете номер")
    await state.update_data(menu=menu)
    await state.set_state(FormActions.group_sending)
    await message.delete()

@msg_router.message(FormActions.program_resending)
async def program_recapture(message: types.Message, state: FSMContext):
    await state.update_data(user_program=message.text)
    data: dict = await state.get_data()
    try:
        menu: types.CallbackQuery = data["menu"]
    except KeyError: pass
    
    await form_displaying(data=data, menu=menu, state=state, message=message)

@msg_router.message(FormActions.group_sending)
async def group_capture(message: types.Message, state: FSMContext):
    await state.update_data(user_group=message.text)
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    
    menu = await menu.edit_text(text=f"""Укажите электронную почту, на которую будет отправлен ответ специалиста.\n\nУбедительная просьба отправлять почту с указанием специального символа - '@'!""")
    await state.update_data(menu=menu)    
    await state.set_state(FormActions.mail_sending)
    await message.delete()

@msg_router.message(FormActions.group_resending)
async def group_recapture(message: types.Message, state: FSMContext):
    await state.update_data(user_group=message.text)
    data: dict = await state.get_data()
    try:
        menu: types.CallbackQuery = data["menu"]
    except KeyError: pass
    
    await form_displaying(data=data, menu=menu, state=state, message=message)

@msg_router.message(FormActions.mail_resending, F.text.contains("@"))
async def mail_recapture(message: types.Message, state: FSMContext):
    await state.update_data(printed_mail=message.text)
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    
    await form_displaying(data=data, menu=menu, state=state, message=message)

@msg_router.message(FormActions.mail_sending, F.text.contains("@"))
async def mail_capture(message: types.Message, state: FSMContext):
    await state.update_data(printed_mail=message.text)
    data: dict = await state.get_data()
    menu: types.CallbackQuery = data["menu"]
    await state.update_data(menu=menu)
    
    await form_displaying(data=data, menu=menu, state=state, message=message)
        
@msg_router.message(FormActions.photo_sending, (F.photo) | (F.document))
@limit_checker
async def photo_attaching(message: types.Message, state: FSMContext):
    from DataStorage import DataStorage
    
    data: dict = await state.get_data()
    photo_id = message.photo[-1].file_id

    await message.delete()
    
    try:
        media_group: MediaGroupBuilder = DataStorage.objects.get(f"media_group_obj#{message.from_user.id}")
        media_group.add_photo(photo_id)
    except (KeyError, AttributeError):
        media_group = MediaGroupBuilder(caption="Фотографии, готовые к прикреплению")
        media_group.add_photo(photo_id)
        DataStorage.objects.update([(f"media_group_obj#{message.from_user.id}", media_group)])
         
    try:
        [await elem.delete() for elem in data["media_group_msg"]]
        media_group_msg = await bot.send_media_group(chat_id=message.from_user.id, media=media_group.build())
        await state.update_data(media_group_msg=media_group_msg)
    except (TelegramBadRequest, KeyError):
        media_group_msg = await bot.send_media_group(chat_id=message.from_user.id, media=media_group.build())
        await state.update_data(media_group_msg=media_group_msg)
    
@msg_router.message(lambda x: x)
async def spam_delete(message: types.Message):
    await message.delete()
    