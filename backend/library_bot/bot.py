# Settings
import os
import sys
from datetime import datetime

import django
from asgiref.sync import sync_to_async

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
django.setup()

# Application
import logging
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup

)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    InlineQueryHandler
)

from library_bot.user_interface.faq import get_faq

from library_bot.user_interface.borrowings import (
    my_borrowings,
    active_borrow,
    get_borrowing_archive
)

from library_bot.user_interface.books import (
    inline_book_search,
    show_book_search_hint
)

from library_bot.user_interface.stages import *

User = get_user_model()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

#Update telegram chat id of the user
async def get_user_by_email(email):
    """Fetches a user from the database by their email."""
    return await sync_to_async(lambda: User.objects.filter(email=email).first())()

async def get_user_by_tg_chat(tg_chat):
    """Fetches a user from the database by their telegram chat id."""
    return await sync_to_async(lambda: User.objects.filter(tg_chat=tg_chat).first())()

async def update_user(user, tg_chat, date_joined):
    """Update data about user"""
    user.tg_chat = tg_chat
    user.date_joined = date_joined
    await sync_to_async(user.save)()

async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Checks if the email exists, updates the user's Telegram ID if found,
    and sends a confirmation or error message.
    """
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

#Start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Checks if the user exists based on Telegram chat ID.
    If the user has an email, proceeds to the welcome post.
    Otherwise, prompts the user to enter their email address.
    """
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

#Main post
async def welcome_post(update: Update, context: CallbackContext) -> None:
    """
    Displays the main menu with borrowing, book search, payment, and FAQ options.
    Edits the message if triggered via a button, otherwise sends a new message.
    """
    query = update.callback_query

    keyboard = [
        [
            InlineKeyboardButton("My borrowings", callback_data="MY_BORROWINGS"),
            InlineKeyboardButton("Books", callback_data="BOOKS"),
        ],
        [InlineKeyboardButton("Pay borrow", callback_data="PAY_BORROW"),],
        [InlineKeyboardButton("FAQ", callback_data="FAQ")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if query and query.message:
        await query.message.edit_text(
            "Welcome to our greatest library.📚\n"
            "Here you can find your borrowings and pay it.🔎\n"
            "Go to FAQ to see the common questions.❓",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Welcome to our greatest library.📚\n"
            "Here you can find your borrowings and pay it.🔎\n"
            "Go to FAQ to see the common questions.❓",
            reply_markup=reply_markup
        )

    return START_ROUTES

def main():
    """
    Initializes and runs the Telegram bot.

    - Loads environment variables.
    - Builds the bot application using the Telegram token.
    - Defines handlers for commands, callbacks, and inline queries.
    - Uses a conversation handler to manage different bot states.
    - Starts polling to continuously receive updates from users.

    Handlers:
    - /start: Begins the conversation and prompts for email if necessary.
    - /welcome_post: Displays the main menu with borrowing options.
    - InlineQueryHandler: Handles inline book searches.
    - CallbackQueryHandlers: Manage navigation through borrowings, book search, FAQ, and returning to the main menu.
    - MessageHandler: Captures text messages to receive user emails.

    The bot listens for user interactions and responds accordingly.
    """

    load_dotenv()
    app = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()
    inline_query_handler = InlineQueryHandler(inline_book_search)
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
                CallbackQueryHandler(get_borrowing_archive, pattern="ARCHIVE"),
                CallbackQueryHandler(show_book_search_hint, pattern="BOOKS"),
                CallbackQueryHandler(get_faq, pattern="FAQ"),
                CallbackQueryHandler(welcome_post, pattern="WELCOME_POST"),

            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(inline_query_handler)
    app.add_handler(conv_handler)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()