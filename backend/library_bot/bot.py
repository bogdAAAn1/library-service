# Settings

import os
import sys
import django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")
django.setup()

# Application
import logging
from django.contrib.auth import get_user_model
from datetime import datetime
from dotenv import load_dotenv
from asgiref.sync import sync_to_async

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

from library_bot.user_interface.borrowings import (
    my_borrowings,
    active_borrow
)

from library_bot.user_interface.books import (
    inline_book_search,
    show_book_search_hint
)


User = get_user_model()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Stages
START_ROUTES, MY_BORROWINGS, BOOKS, PAY_BORROW, FAQ, ACTIVE_BORROW, ARCHIVE = range(7)

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

async def welcome_post(update: Update, context: CallbackContext) -> None:
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
                # CallbackQueryHandler(archive_borrowings, pattern="ARCHIVE"),
                CallbackQueryHandler(show_book_search_hint, pattern="BOOKS"),
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