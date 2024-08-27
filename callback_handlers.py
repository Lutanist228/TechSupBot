from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.exceptions import TelegramBadRequest

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
                await callback.message.edit_text(text="""Проверьте, пожалуйста, регистр и язык ввода логина и пароля.\n\nТребуется ли консультация специалиста или проблема решена?""", reply_markup=User_Keyboards.category())
            case 2 | 5: 
                await state.update_data(chosen_category=category_table[category_id - 1])
                await callback.message.edit_text(text="""Проверьте программу, на которую Вы записаны, возможно, этот раздел не входит в рамки обучения.\n\nТребуется ли консультация специалиста или проблема решена?""", reply_markup=User_Keyboards.category())
            case 3 | 4:
                await state.update_data(chosen_category=category_table[category_id - 1])
                await callback.message.edit_text(text="""Требуется ли консультация специалиста или проблема решена?""", reply_markup=User_Keyboards.category())
                
@cb_router.callback_query(FormActions.form_claiming)
async def form_claiming(callback: types.CallbackQuery, state: FSMContext):
    from DataStorage import DataStorage

    data: dict = await state.get_data()
    mail_sender = DataStorage.temp_data_1
    
    try:
        category_table = data["category_table"] 
        chosen_category = data["chosen_category"] ; form_topic = chosen_category["Категории"]
    except KeyError: pass
    
    if callback.data == "send_form":
        DataStorage.temp_data_2 = None
        try:
            [await elem.delete() for elem in data["media_group_msg"]]
        except KeyError: pass
        
        mail_sender.subject = form_topic
        mail_sender.letter_text = f"""ID пользователя: {callback.from_user.id}\nФИО пользователя: {data["user_fio"]}\nПочта пользователя: {data["printed_mail"]}\nПрограмма и группа пользователя: {data["user_program"]} / {data["user_group"]}\n\nСодержание: {data["printed_text"]}"""
        
        await mail_sender.create_message()
        await mail_sender.send_email(state)
        
        await state.clear()
        await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
        message = await callback.message.answer("Заявка успешно сформирована. Ожидайте ответ на указанный e-mail")
        await message_delition(message)
    elif callback.data == "attach_photo":
        DataStorage.temp_data_2 = None
        try:
            [await elem.delete() for elem in data["media_group_msg"]]
        except KeyError: pass
        
        await state.update_data(media_group_msg=[])
        await state.set_state(FormActions.photo_sending)
        menu: types.CallbackQuery = await callback.message.edit_text(text="Отправьте скриншот(-ы) вашей проблемы. Вы можете прикрепить до 3-х фото к вашей заявке.\nДля завершения операции нажмите - 'Прикрепить фото'.\nДля отмены операции нажмите - 'Вернуться к заявке'", reply_markup=User_Keyboards.form_edit(True))
        await state.update_data(menu=menu)
    elif callback.data == "edit_form":
        await state.set_state(FormActions.form_editing)
        await callback.message.edit_text(text="Выберете, какую часть заявки необходимо отредактировать", reply_markup=User_Keyboards.form_edit())
    elif callback.data == "main_menu":
        DataStorage.temp_data_2 = None
        try:
            [await elem.delete() for elem in data["media_group_msg"]]
        except KeyError: pass
        
        await state.update_data(media_group_msg=[])
        
        await state.clear()
        await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
    
@cb_router.callback_query(FormActions.form_editing)
async def form_editing(callback: types.CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    try:
        category_table = data["category_table"] 
        chosen_category = data["chosen_category"] ; form_topic = chosen_category["Категории"]
    except KeyError: pass
    edit_object: str = callback.data.split("_")[0]
    
    match edit_object:
        case "content":
            await callback.message.edit_text(text=f"""Тема Вашего обращения: {chosen_category["Категории"]}\n\nСформируйте текстовое обращение по указанной Вами проблеме и отправьте его в чат с ботом""")        
            await state.set_state(FormActions.text_resending)
        case "mail":
            await callback.message.edit_text(text="""Укажите электронную почту, на которую будет отправлен ответ специалиста.\n\nУбедительная просьба отправлять почту с указанием специального символа - '@'!""")
            await state.set_state(FormActions.mail_resending)
        case "program":
            await callback.message.edit_text(text="""Укажите наименование Вашей программы обучения""")
            await state.set_state(FormActions.program_resending)
        case "group":
            await callback.message.edit_text(text="""Укажите Вашу группу, если знаете номер""")
            await state.set_state(FormActions.group_resending)
        case "fio":
            await callback.message.edit_text(text="""Укажите Ваше ФИО. Просим отправить ФИО одним сообщением""")
            await state.set_state(FormActions.fio_resending)
        case "category":
            await state.set_state(FormActions.category_choosing)
            await callback.message.edit_text(text="Выберете категорию заявки", reply_markup=await User_Keyboards.categories(state))
        case "return":
            await state.set_state(FormActions.form_claiming)
            await form_displaying(data=data, state=state, message=callback.message)

@cb_router.callback_query(FaqActions.surfing_faq)
async def surfing_faq(callback: types.CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    op_type, current_page = callback.data.split(":") ; current_page = int(current_page)
    pages: int = data["pages"]; ITEMS_PER_PAGE = 10
    remaining_faq: dict = data["remaining_faq"]
    full_faq: dict = data["full_faq"]
    
    async def form_faq(msg_text: str, reassign_remaining: bool = True): 
        nonlocal pages
        nonlocal ITEMS_PER_PAGE
        
        await state.update_data(remaining_faq=remaining_faq[ITEMS_PER_PAGE:]) if reassign_remaining == True else ...
        await callback.message.edit_text(text=msg_text, reply_markup=User_Keyboards.surfing_faq(max_page=pages, exeption_raised=True, page_num=current_page), parse_mode="HTML")
    
    if op_type == "faq_next":
        try:
            current_faq, msg_text = parse_faq(json_info=remaining_faq[:ITEMS_PER_PAGE], multiplier=10 * (current_page - 1))
            await form_faq(msg_text)
        except IndexError:
            index = len(remaining_faq)
            current_faq, msg_text = parse_faq(json_info=remaining_faq[:index], multiplier=10 * (current_page - 1))
            await form_faq(msg_text, False)
    elif op_type == "faq_prev":
        current_faq, msg_text = parse_faq(json_info=full_faq[(current_page - 1) * ITEMS_PER_PAGE:((current_page - 1) * ITEMS_PER_PAGE) + 10], multiplier=10 * (current_page - 1)) 
        remaining_faq = full_faq[current_page * ITEMS_PER_PAGE:]
        await state.update_data(remaining_faq=remaining_faq)
        await form_faq(msg_text, False)
    elif op_type == "main_menu":
        await state.clear()
        await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
    
@cb_router.callback_query(FormActions.photo_sending)
async def photo_operations(callback: types.CallbackQuery, state: FSMContext):
    from DataStorage import DataStorage
    data: dict = await state.get_data()
    
    if callback.data == "return_to_form":
        [await elem.delete() for elem in data["media_group_msg"]]
        DataStorage.temp_data_2 = None
        await state.update_data(media_group_msg=[])
        
        await state.set_state(FormActions.form_claiming)
        await form_displaying(data=data, state=state, message=callback.message)
    elif callback.data == "attach_photos":
        await data["media_group_msg"][0].edit_caption(caption="Фотографии, прикреплённые к заявке")
        await state.set_state(FormActions.form_claiming)
        await form_displaying(data=data, state=state, message=callback.message)
        
@cb_router.callback_query()
async def define_processes(callback: types.CallbackQuery, state: FSMContext):
    process = callback.data
    data: dict = await state.get_data()
    
    match process:
        case "main_menu:0":
            await state.clear()
            await callback.message.edit_text(text="Здравствуйте, чем могу помочь?", reply_markup=User_Keyboards.main_menu())
        case "create_form":
            await state.set_state(FormActions.category_choosing)
            await callback.message.edit_text(text="Выберете категорию заявки", reply_markup=await User_Keyboards.categories(state))
        case "info_block":
            message = await callback.message.answer(text="Ваша ссылка на материалы блока 'Информация' - http://sechenov.lpt.digital/cabinet/info/?login=yes")
            await message_delition(message, time_sleep=1800) # сообщения-уведомления удаляются каждые 30 минут
        case "faq_block":
            full_faq, msg_text = parse_faq()
            ITEMS_PER_PAGE = 10
            pages: int = len(full_faq) // ITEMS_PER_PAGE
            
            async def form_faq(): 
                nonlocal msg_text
                nonlocal pages
                nonlocal ITEMS_PER_PAGE
                
                try:
                    await callback.message.edit_text(text=msg_text, reply_markup=User_Keyboards.surfing_faq(), parse_mode="HTML")
                except TelegramBadRequest:
                    await state.set_state(FaqActions.surfing_faq)
                    await state.update_data(full_faq=full_faq, pages=pages)
                    current_faq, msg_text = parse_faq(json_info=full_faq[:ITEMS_PER_PAGE])
                    await state.update_data(remaining_faq=full_faq[ITEMS_PER_PAGE:])
                    await callback.message.edit_text(text=msg_text, reply_markup=User_Keyboards.surfing_faq(exeption_raised=True), parse_mode="HTML")
                    
            await form_faq()
        case "feedback_block":
            await state.set_state(FormActions.text_sending)
            await state.update_data(chosen_category="Обратная связь")
            menu = await callback.message.edit_text(text=f"""Тема Вашего обращения: Обратная связь\n\nСформируйте текстовое обращение для обратной связи и отправьте его в чат с ботом""")
            await state.update_data(menu=menu)
        