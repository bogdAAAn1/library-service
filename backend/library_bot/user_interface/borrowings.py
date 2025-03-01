import logging
from datetime import datetime

from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from borrowing.models import Borrowing

# Stages
START_ROUTES, MY_BORROWINGS, BOOKS, PAY_BORROW, FAQ, ACTIVE_BORROW, ARCHIVE = range(7)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

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