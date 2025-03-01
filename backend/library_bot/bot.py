import asyncio
import os
import sys
from datetime import datetime

import django
from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from dotenv import load_dotenv
from django.contrib.auth import get_user_model

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler, \
    ContextTypes, MessageHandler, filters



# Settings
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
django.setup()

from borrowing.models import Borrowing

User = get_user_model()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def get_user_by_email(email):
    return await sync_to_async(lambda: User.objects.filter(email=email).first())()

async def get_user_by_tg_chat(tg_chat):
    return await sync_to_async(lambda: User.objects.filter(tg_chat=tg_chat).first())()

async def update_user(user, tg_chat, date_joined):
    user.tg_chat = tg_chat
    user.date_joined = date_joined
    await sync_to_async(user.save)()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id

    user = await get_user_by_tg_chat(user_id)

    if user:
        if user.email:
            await welcome_post(update, context)
            return START_ROUTES
        else:
            await update.message.reply_text("Hi! Enter your email address.")
    else:
        await update.message.reply_text("Hi! Enter your email address.")
    return

async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    email = update.message.text
    user_id = update.message.chat.id

    user = await get_user_by_email(email)

    if user:
        await update_user(user, user_id, datetime.now())
        await update.message.reply_text("Your telegram account has been updated.")
        await welcome_post(update, context)
        return START_ROUTES

    else:
        await update.message.reply_text("Email doesn't exist.")
        return CommandHandler.END


START_ROUTES, MY_BORROWINGS, BOOKS, PAY_BORROW, FAQ, ACTIVE_BORROW, ARCHIVE = range(7)

async def welcome_post(update: Update, context: CallbackContext) -> None:

    keyboard = [
        [
            InlineKeyboardButton("My borrowings", callback_data="MY_BORROWINGS"),
            InlineKeyboardButton("Books", callback_data="BOOKS"),
        ],
        [InlineKeyboardButton("Pay borrow", callback_data="PAY_BORROW"),],
        [InlineKeyboardButton("FAQ", callback_data="FAQ")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome to our greatest library.📚\n"
        "Here you can find your borrowings and pay it.🔎\n"
        "Go to FAQ to see the common questions.❓",
        reply_markup=reply_markup)

    return START_ROUTES

async def my_borrowings(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    logger.info("MY_BORROWINGS button clicked")
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("Active borrow", callback_data="ACTIVE_BORROW"),
            InlineKeyboardButton("Archive", callback_data="ARCHIVE"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Here you can see your active borrowings or books you already returned.", reply_markup=reply_markup
    )
    return START_ROUTES


async def get_overdue_borrow(user_id):
    logger.info(f"Checking overdue borrowings for user_id: {user_id}")

    return await sync_to_async(
        lambda: Borrowing.objects.filter(
            expected_return_date__lt=datetime.now(), user__tg_chat=user_id
        ).select_related('book')
        .first()
    )()


async def active_borrow(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Here you can see your active borrow.")

    user = update.callback_query.message.chat.id
    logger.info(f"User ID: {user}")

    book_user_borrowed = await get_overdue_borrow(user)
    logger.info(f"Book borrowed: {book_user_borrowed}")

    if book_user_borrowed:
        await query.edit_message_text(
            f"You have an active borrow!\n"
            f"Book: {book_user_borrowed.book.title}\n"
            f"Expected return date: {book_user_borrowed.expected_return_date}"
        )
    else:
        await query.edit_message_text(f"No borrowing available.")

def main():
    load_dotenv()
    app = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("welcome_post", welcome_post),
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email),
        ],
        states={
            START_ROUTES: [
                CallbackQueryHandler(my_borrowings, pattern="MY_BORROWINGS"),
                CallbackQueryHandler(active_borrow, pattern="ACTIVE_BORROW"),
                # CallbackQueryHandler(archive_borrowings, pattern="ARCHIVE"),

            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()