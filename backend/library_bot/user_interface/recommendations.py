import random

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext

from book.models import Book
from library_bot.user_interface.buttons import send_back_button


async def get_random_book(update: Update, context: CallbackContext) -> Book:
    sum_of_books = await sync_to_async(Book.objects.count)()
    random_index = random.randint(0, sum_of_books - 1)
    recommended_book = await sync_to_async(lambda: Book.objects.all()[random_index])()
    return recommended_book

async def send_recommend_book(update: Update, context: CallbackContext) -> None:
    recommended_book = await get_random_book(update, context)

    await update.callback_query.message.reply_text(
        "*Here is your recommended book for today:*\n\n"
        f"*Book*: {recommended_book.title}\n"
        f"*Author*: {recommended_book.author}\n\n"
        "*Description*: Lorem ipsum dolor sit amet, consectetuer",
        parse_mode="MARKDOWN",
    )

    await send_back_button(update.callback_query)