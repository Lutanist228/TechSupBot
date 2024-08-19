from dotenv import load_dotenv
from aiogram import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio as asy
import os
import json

from objects import MailSender

load_dotenv()

dp = Dispatcher(storage=MemoryStorage())
bot = Bot(os.getenv("API_TOKEN"))

async def on_startup():
    from DataStorage import DataStorage
    global mail_sender
    mail_sender, status = await MailSender(sender=os.getenv("BOT_MAIL"), bot=bot, receiver=os.getenv("SUPPORT_MAIL"),password=os.getenv("OUTER_PASSWORD")).connect(port=os.getenv("SMTP_PORT"))
    DataStorage.temp_data = mail_sender
    print("Бот запущен.")    
    
async def on_shutdown():
    await mail_sender.close_connection()
    print('Бот выключен.')

async def main():
    import message_handlers, callback_handlers
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(message_handlers.msg_router, callback_handlers.cb_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asy.run(main())

