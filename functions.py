import csv
import asyncio as asy 
from aiogram.fsm.context import FSMContext
from aiogram import types

from states import *
from keyboards import *

# def create_csv(file_path: str) -> csv.excel:
#     with open(file_path, "w", encoding="utf-8", newline="") as file:
#         writer = csv.writer(file)
#         writer.writerows(
#             categories
#         )
        
async def message_delition(*args, time_sleep = 20):
        await asy.sleep(time_sleep)
        for arg in args:
            await arg.delete()

def save_to_txt(file_path: str = "", print_as_finished = True, save_mode: str = "a", **kwargs):
        
        r"""Функция save_to_txt принимает в себя:
        1) file_path - путь к файлу в формате: C:\Users\user\*file_dir*\. в случае, если нет необходимости 
        сохранять файл в конкретную директорию, то файл сохраняется в директорию скрипта с save_to_txt;
        2) print_as_finished - флаг, который контролирует вывод надписи The information has been added to the {file_name}.txt file.;
        3) save_mode - формат работы с .txt файлом, по умолчанию - 'a';
        4) **kwargs - основа функции, где key - название файла, а value - содержимое файла;
        """
        for key, value in kwargs.items():
            file_name = key
            with open(rf"{file_path}{file_name}.txt", mode=save_mode, buffering=-1, encoding="utf-8") as file:
                if isinstance(value, (tuple, list)):
                    [file.write(val) for val in value]
                else:
                    file.write(str(value))
            if print_as_finished == True:
                print("\n")
                print(f"The information has been added to the {file_name}.txt file.")
                           
def parse_faq(json_info = None, multiplier: int = 0) -> str:
    from objects import DataParser
    
    msg_text = ""
    
    if json_info == None:
        json_parser = DataParser("faq.json", "json")
        json_info = json_parser.read_info()
    
    for number, row in enumerate(json_info):
        question, answer = f"question_{number + multiplier + 1}", f"answer_{number + multiplier + 1}"
        msg_text += f"{row[question]}\n{row[answer]}\n\n" 
    
    return json_info, msg_text

async def form_displaying(data: dict,state: FSMContext, message: types.Message, menu: types.CallbackQuery = None):
    chosen_category = data["chosen_category"] ; form_topic = chosen_category["Категории"]
    printed_mail = data["printed_mail"]
    printed_text = data["printed_text"]
    user_fio = data["user_fio"]
    educ_program = data["user_program"]
    educ_group = data["user_group"]
    
    if menu is not None:
        await message.delete()
        await menu.edit_text(text=f"""Проверьте, пожалуйста, введенные Вами данные.\n\nТема обращения: {form_topic}\nПочта отправителя: {printed_mail}\nФИО отправителя: {user_fio}\nПрограмма обучения: {educ_program}\nГруппа: {educ_group}\nСодержание обращения: {printed_text}""", reply_markup=User_Keyboards.category(True))
    else:
        await message.edit_text(text=f"""Проверьте, пожалуйста, введенные Вами данные.\n\nТема обращения: {form_topic}\nПочта отправителя: {printed_mail}\nФИО отправителя: {user_fio}\nПрограмма обучения: {educ_program}\nГруппа: {educ_group}\nСодержание обращения: {printed_text}""", reply_markup=User_Keyboards.category(True))
    
    await state.set_state(FormActions.form_claiming)

def limit_checker(func):
    async def wrapper(*args, **kwargs):
        state: FSMContext = kwargs['state']
        data: dict = await state.get_data()
        message: types.Message = args[0]
        
        try:
            if message.document.file_id:
                msg = await message.answer(text="Просим вас переотправить фотографию, но с выставленной опцией 'Compress the image'\\'Сжать изображение'")
                await message.delete()
                return await message_delition(msg, time_sleep=5)
        except AttributeError:
            pass

        try:
            if len(data["media_group_msg"]) >= 3:
                msg = await message.answer(text="Вы достигли лимита для прикрепления фотографий")
                await message.delete()
                return await message_delition(msg, time_sleep=5)
            else:
                return await func(message, state)
        except KeyError:
            return await func(message, state)
        
    return wrapper


