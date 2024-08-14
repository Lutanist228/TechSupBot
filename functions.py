import csv
from config import *
import asyncio as asy 

def create_csv(file_path: str) -> csv.excel:
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(
            categories
        )
        
async def message_delition(*args, time_sleep = 20):
        await asy.sleep(time_sleep)
        for arg in args:
            await arg.delete()
