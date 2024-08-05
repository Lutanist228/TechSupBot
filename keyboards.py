from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from objects import DataParser

# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------
class User_Keyboards():
    
    def main_menu() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        
        btn_form = InlineKeyboardButton(text='Сформировать заявку', callback_data='create_form')
        btn_info = InlineKeyboardButton(text="Материалы блока 'Информация'", callback_data="info_block")
        btn_faq = InlineKeyboardButton(text="Часто задаваемые вопросы и ответы", callback_data="faq_block")
        btn_feedback = InlineKeyboardButton(text="Обратная связь", callback_data="feedback_block")
        
        keyboard.add(btn_form, btn_info, btn_faq, btn_feedback)
        keyboard.adjust(1, repeat=True)
        
        return keyboard.as_markup()

    def categories() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        buttons = list()
        categories = DataParser("categories.csv", "csv").read_info()
        
        for row in categories:
            row: dict
            buttons.append(InlineKeyboardButton(text=f"{row.get("Категории")}", callback_data=f"cat_id={row.get("id")}"))
            
        keyboard.add(*buttons)
        keyboard.adjust(1, repeat=True)
        
        return keyboard.as_markup()

# ----------------------------------------------U-S-E-R-T-P-A-N-E-L----------------------------------------------

