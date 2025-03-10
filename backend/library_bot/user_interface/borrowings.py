import logging
from datetime import datetime

from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from borrowing.models import Borrowing
from library_bot.user_interface.buttons import send_back_button

(
    START_ROUTES,
    BOOKS,
    MY_BORROWINGS,
    ACTIVE_BORROW,
    ARCHIVE,
    FAQ,
    RANDOM_BOOK) = range(7)


async def my_borrowings(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "Active borrow 📃",
                callback_data="ACTIVE_BORROW"
            ),
            InlineKeyboardButton(
                "Archive 🗄",
                callback_data="ARCHIVE"
            ),
        ],
        [InlineKeyboardButton("◀️ Back", callback_data="WELCOME_POST")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Here you can see your active "
             "borrowings or books you already returned.",
        reply_markup=reply_markup,
    )
    return START_ROUTES


async def get_overdue_borrow(user_id):
    return await sync_to_async(
        lambda: Borrowing.objects.filter(
            expected_return_date__lte=datetime.now(), user__tg_chat=user_id
        )
        .select_related("book")
        .first()
    )()


async def active_borrow(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Here you can see your active borrow.")

    user = update.callback_query.message.chat.id
    book_user_borrowed = await get_overdue_borrow(user)

    if book_user_borrowed:
        await query.edit_message_text(
            f"*You have an active borrow!*\n\n"
            f"*Book*: {book_user_borrowed.book.title}\n"
            f"*Expected return date*: "
            f"{book_user_borrowed.expected_return_date}",
            parse_mode="MARKDOWN",
        )
    else:
        await query.edit_message_text("No borrowing available.")

    await send_back_button(update.callback_query)


async def get_borrows_list(user_id):
    return await sync_to_async(
        lambda: list(
            Borrowing.objects.filter(
                expected_return_date__lt=datetime.now(), user__tg_chat=user_id
            ).select_related("book")
        )
    )()


async def get_borrowing_archive(
        update: Update,
        context: CallbackContext
) -> None:
    user = update.callback_query.message.chat.id
    message = update.message if update.message \
        else update.callback_query.message
    borrowing_list = await get_borrows_list(user)
    filtered_borrowings = [borrow for borrow in borrowing_list]

    for each_borrow in filtered_borrowings:
        await message.reply_text(
            f"*Borrow date:* {each_borrow.borrow_date}\n\n"
            f"*Book author:* {each_borrow.book.author}\n"
            f"*Book title:* {each_borrow.book.title}\n\n"
            f"*Expected return date:* {each_borrow.expected_return_date}\n"
            f"*Actual return date:* {each_borrow.actual_return_date}",
            parse_mode="MARKDOWN",
        )

    await send_back_button(update.callback_query)
