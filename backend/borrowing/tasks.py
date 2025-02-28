import asyncio
import os

from celery import shared_task
from dotenv import load_dotenv
from telegram import Bot

from borrowing.models import Borrowing

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
chat_id = "-1002269497388"

@shared_task
def morning_borrow_update() -> int:
    sum_of_all_borrows = Borrowing.objects.count()
    if sum_of_all_borrows > 0:
        message = f"Today we have {sum_of_all_borrows} borrowings."
    else:
        message = f"Today we have no borrowings."

    async def send():
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)

    asyncio.run(send())

@shared_task
def send_notification_to_telegram(message):
    async def send():
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)

    asyncio.run(send())
