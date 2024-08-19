import csv
import json
import smtplib
import imaplib
from aiogram import types
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import email
from email.parser import Parser
from email.policy import default
from pprint import pprint
from datetime import datetime as dt
from dotenv import load_dotenv
import os
from aiogram import Bot
from aiogram import exceptions

from keyboards import *
from functions import *

load_dotenv()

class DataParser():
    def __init__(self, path: str, format: str) -> None:
        self.path = path
        self.format = format
        
    def read_info(self):
        data = []
        
        with open(self.path, "r", encoding="utf-8") as file:
            match self.format:
                case "csv":
                    reader = csv.DictReader(file)
                    for row in reader:
                        data.append(row)
                    return data
                case "json":
                    data = json.load(file)
                    return [data[row] for row in data]
                    
class DataTypeError():
    def __init__(self, error_message: str) -> None:
        self.raise_error(error_message)
        
    def raise_error(error_message: str) -> None:
        return print(error_message)
        
class MailSender():
    
    def __init__(self, sender: str, password: str, receiver: str, bot: Bot,  subject: str = None, letter_text: str = None) -> None:
        self.sender = sender
        self.password = password 
        self.receiver = receiver 
        self.subject = subject
        self.letter_text = letter_text
        self.bot = bot
        self.port = None
        self.message = None
        self.server = None
        self.error_report = dict()
        
    async def connect(self, port: int, timeout: int = 10) -> smtplib.SMTP_SSL:
        conn_status = False
        
        try:
            server = smtplib.SMTP_SSL('smtp.yandex.com', port, timeout=timeout)
            server.ehlo()
            server.login(self.sender, self.password)
            self.server = server
            print("Произведено успешное подключение к почтовому клиенту.")
            conn_status = True
        except TimeoutError as err:
            print("Было превышено ожидание подключения к серверу: ", err)
            print("Попытка повторного подключения к серверу...")
            self.error_report.update([("TimeoutError", err)])
            await self.connect(port=port, timeout=timeout)
        except smtplib.SMTPServerDisconnected as err:
            print("Соединение с сервером прервалось: ", err)
            print("Попытка повторного подключения к серверу...")
            self.error_report.update([("SMTPServerDisconnected", err)])
            await self.connect(port=port, timeout=timeout)
        except Exception as exeption: 
            print("Произошла неизвестная ошибка: ", exeption) 
            print("Попытка повторного подключения к серверу...")
            self.error_report.update([("UnknownExeption", exeption)])
            await self.connect(port=port, timeout=timeout)
            
        self.port = port
        return self, conn_status
        
    async def close_connection(self):
        self.server.close()    
        print("Успешное отключение от почтового клиента.")
        
    async def create_message(self) -> MIMEText:

        message = (MIMEText(self.letter_text, "plain", "utf-8"))
        message["From"] = self.sender
        message["To"] = self.receiver
        message["Subject"] = Header(self.subject, "utf-8") # id телеграмма
        
        self.message = message
        return self
    
    async def send_email(self, state: FSMContext, message: types.Message = None) -> None:
        await self.__reconnecting(message=message, state=state)
        
        try:
            self.server.sendmail(self.sender, self.receiver, self.message.as_string())
            print(f"Письмо было успешно отправлено по адресу {self.receiver} от {self.sender}")
        except smtplib.SMTPServerDisconnected:
            await self.connect(port=self.port)
            print(f"Повторная отправка письма...")
            await self.send_email(state)
        except smtplib.SMTPDataError: 
            print(f"Письмо было отложено на 30 секунд из-за подозрений в спаме.")
            await asy.sleep(30)
            print(f"Повторная отправка письма...")
            await self.send_email(state)
            
    async def __reconnecting(self, message: types.Message, state: FSMContext) -> None:
        attempts = 0
        data: dict = await state.get_data()
        try:
            menu: types.CallbackQuery = data["menu"]
        except KeyError: pass
        
        while self.server == None:
            if attempts == 5:
                print("Сервер отказал в подключении.")
                MODERATOR_ID = os.getenv("MODERATOR_ID")
                
                await self.bot.send_message(chat_id=MODERATOR_ID, text=f"{"-"*50}\n\nПроизошла критическая ошибка подключения к серверу от {dt.now()}.")
                for item in self.error_report.items():
                    await self.bot.send_message(chat_id=MODERATOR_ID, text=f"{item[0]}: {item[1]}")     
                
                try:
                    await menu.edit_text(text="Произошла ошибка при отправке вашей заявки на почту технической поддержки. Сообщение об ошибке было направлено модератору чат-бота. Просим вас повторить отправку позже.", reply_markup=User_Keyboards.backing_to_menu())   
                    await message.delete() if message != None else ...
                except exceptions.TelegramBadRequest: pass
                
            attempts += 1
            print(f"Попытка подключения №{attempts}...")
            server_obj, status = await self.connect(port=self.port)
        
        else:
            print(f"Успешное переподключение к серверу...")
              
class MailParser():
    def __init__(self, mail_login: str, mail_password: str) -> None:
        self.mail_login = mail_login
        self.mail_password = mail_password 
        self.server = None   
        
    def connect(self, port: int, timeout: int = 10) -> imaplib.IMAP4_SSL:
        try:
            server = imaplib.IMAP4_SSL('imap.yandex.com', port, timeout=timeout)
            server.login(self.mail_login, self.mail_password)
            self.server = server
        except Exception as e:
            print("Ошибка подключения -", e)
            print("Попытка повторного подключения к серверу...")
            self.connect(port=port, timeout=timeout)
        
        return self
        
    def close_connection(self):
        self.server.close()    
        
    def return_section_data(self, section: str = "INBOX") -> tuple:
        self.server.select(section)
        status, data = self.server.search(None, "ALL")
        
        id_list = data[0] ; id_list = id_list.split()
        id_list = list(map(lambda x: x.decode('utf-8'), id_list))
        
        return status, id_list
    
    def return_msg_data(self, msg_id: int) -> dict:
        message = dict()
        
        result, data = self.server.fetch(msg_id, "(RFC822)")
        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)
        
        headers = Parser(policy=default).parsestr(raw_email_string)
        body = headers.get_body(preferencelist=('plain', 'html'))
            
        message.update([('From', headers['from'])])
        message.update([('To', headers['to'])])
        message.update([('Date', email_message['Date'])])
        message.update([('Subject', headers['subject'])])
        message.update([('Content', ''.join(body.get_content().splitlines(keepends=False)[:3]))])
        message.update([('Message-Id', email_message['Message-Id'])])
        message.update([('Message-Number', int(msg_id))])

        pprint(message, sort_dicts=False)
        
        return message
   