import asyncio
import os
import random

from celery import shared_task
from django.contrib.auth import get_user_model
from telegram import Bot
from book.models import Book

token = os.getenv("TELEGRAM_TOKEN")

User = get_user_model()

@shared_task
def send_book_of_the_week():

    sum_of_books = Book.objects.count()
    random_index = random.randint(0, sum_of_books - 1)
    recommended_book = Book.objects.all()[random_index]

    message = (
        "Here is Book of the Week:\n\n"
        f"Book: {recommended_book.title}\n"
        f"Author: {recommended_book.author}\n\n"
        "Description: Lorem ipsum dolor sit amet, consectetuer"
    )

    async def send():
        bot = Bot(token=token)
        user_ids = [user.tg_chat for user in User.objects.all()]
        for user_id in user_ids:
            await bot.send_message(chat_id=user_id, text=message)

    asyncio.run(send())
    return "Success"


@shared_task
def new_book_available_notification(message):
    async def send():
        bot = Bot(token=token)
        user_ids = [user.tg_chat for user in User.objects.all()]
        for user_id in user_ids:
            await bot.send_message(chat_id=user_id, text=message)

    asyncio.run(send())
    return "Success"
