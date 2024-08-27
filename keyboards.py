from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

# ----------------------------------------------U-S-E-R-P-A-N-E-L----------------------------------------------
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

    async def categories(state: FSMContext) -> InlineKeyboardMarkup:
        from objects import DataParser, DataTypeError
        keyboard = InlineKeyboardBuilder()
        buttons = list()
        categories = DataParser("categories.csv", "csv").read_info()
        btn_menu_return = InlineKeyboardButton(text="Назад в главное меню", callback_data="main_menu")
        
        try:
            if isinstance(categories, list) != True or isinstance(categories[0], dict) != True:
                raise DataTypeError("формат данных должен соответствовать шаблону [{}, {}, {}]")
            else: pass
        except IndexError:
            raise DataTypeError("формат данных должен соответствовать шаблону [{}, {}, {}]")
        
        await state.update_data(category_table=categories)
        
        for row in categories:
            row: dict
            buttons.append(InlineKeyboardButton(text=f"{row.get('Категории')}", callback_data=f"cat_id={row.get('id')}"))
        buttons.append(btn_menu_return)   
         
        keyboard.add(*buttons)
        keyboard.adjust(1, repeat=True)
        
        return keyboard.as_markup()
    
    def category(is_ended: bool = False) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        
        btn_solved = InlineKeyboardButton(text="Проблема решена", callback_data="cat_state=solved")
        btn_unsolved = InlineKeyboardButton(text="Требуется консультация", callback_data="cat_state=unsolved")
        btn_menu_return = InlineKeyboardButton(text="Назад в главное меню", callback_data="main_menu")
        btn_edit_form = InlineKeyboardButton(text="Отредактировать заявку", callback_data="edit_form")
        btn_attach_photo = InlineKeyboardButton(text="Прикрепить фото", callback_data="attach_photo")
        btn_send_form = InlineKeyboardButton(text="Отправить заявку", callback_data="send_form")
        btn_remove_form = InlineKeyboardButton(text="Отменить отправку", callback_data="main_menu")
        
        if is_ended == False:
            keyboard.add(btn_solved, btn_unsolved, btn_menu_return)
            keyboard.adjust(1, repeat=True)
        else:
            keyboard.add(btn_send_form, btn_attach_photo, btn_edit_form, btn_remove_form)
            keyboard.adjust(1, repeat=True)
            
        return keyboard.as_markup()
    
    def form_edit(is_photo: bool = False) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        
        btn_categories_return = InlineKeyboardButton(text="Изменить категорию", callback_data="category_edit")
        btn_mail_edit = InlineKeyboardButton(text="Изменить почту", callback_data="mail_edit")
        btn_content_edit = InlineKeyboardButton(text="Изменить содержание", callback_data="content_edit")
        btn_program_edit = InlineKeyboardButton(text="Изменить програму", callback_data="program_edit")
        btn_group_edit = InlineKeyboardButton(text="Изменить группу", callback_data="group_edit")
        btn_fio_edit = InlineKeyboardButton(text="Изменить ФИО", callback_data="fio_edit")
        btn_back_to_form = InlineKeyboardButton(text="Вернуться к заявке", callback_data="return_to_form")
        btn_claim_attachements = InlineKeyboardButton(text="Прикрепить фото", callback_data="attach_photos")
        
        if is_photo == False:
            keyboard.add(btn_content_edit, btn_fio_edit, btn_program_edit, btn_group_edit, btn_mail_edit, btn_categories_return, btn_back_to_form)
            keyboard.adjust(2, repeat=True)
        else:
            keyboard.add(btn_claim_attachements, btn_back_to_form)
            keyboard.adjust(1, repeat=True)
        
        return keyboard.as_markup()
    
    def backing_to_menu() -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
                
        keyboard.add(InlineKeyboardButton(text="Назад в главное меню", callback_data="main_menu"))
        keyboard.adjust(1, repeat=True)
        
        return keyboard.as_markup()
    
    def surfing_faq(max_page: int = 0, exeption_raised: bool = False, page_num: int = 1) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        max_page += 1
        
        btn_forward = InlineKeyboardButton(text="Следующая страница", callback_data=f"faq_next:{page_num + 1}")
        btn_back = InlineKeyboardButton(text="Предыдущая страница", callback_data=f"faq_prev:{page_num - 1}")
        btn_menu_return = InlineKeyboardButton(text="Назад в главное меню", callback_data="main_menu:0")
        
        if exeption_raised == True and page_num == 1:
            keyboard.add(btn_forward, btn_menu_return)
        elif exeption_raised == True and page_num == max_page:
            keyboard.add(btn_back, btn_menu_return)
        elif exeption_raised == True and page_num > 1:
            keyboard.add(btn_forward, btn_back, btn_menu_return)
        else:
            keyboard.add(btn_menu_return)
        
        keyboard.adjust(1, repeat=True)
        return keyboard.as_markup()
        
# ----------------------------------------------U-S-E-R-P-A-N-E-L----------------------------------------------

