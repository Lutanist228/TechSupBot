from dotenv import load_dotenv, dotenv_values
from aiogram import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio as asy
import os

load_dotenv()

dp = Dispatcher(storage=MemoryStorage())
bot = Bot(os.getenv("API_TOKEN"))

async def on_startup():
    print("Бот запущен")    
    
async def on_shutdown():
    print('Бот выключен')

async def main():
    import message_handlers, callback_handlers
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(message_handlers.msg_router, callback_handlers.cb_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asy.run(main())

