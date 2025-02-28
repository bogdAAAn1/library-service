import asyncio
import os

from celery import shared_task
from dotenv import load_dotenv
from telegram import Bot

@shared_task
def send_notification_to_telegram():
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = "-1002269497388"
    message = "TestMessage"

    async def send_message():
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)

    asyncio.run(send_message())
