from uuid import uuid4

from asgiref.sync import sync_to_async
from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from book.models import Book

(
    START_ROUTES,
    BOOKS,
    MY_BORROWINGS,
    ACTIVE_BORROW,
    ARCHIVE,
    FAQ,
    RANDOM_BOOK) = range(7)


async def show_book_search_hint(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("Back", callback_data="WELCOME_POST")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "To search books, type @project_librery_bot <book title>.\n"
        "Or press the button below to go back.",
        reply_markup=reply_markup,
    )

    return START_ROUTES


async def get_books():
    return await sync_to_async(lambda: list(Book.objects.all()))()


async def inline_book_search(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.inline_query:
        inline_query = update.inline_query
        query = inline_query.query
        print(f"Search query: {query}")

        if not query:
            return

        book_list = await get_books()
        filtered_books = [
            book for book in book_list if query.lower() in book.title.lower()
        ]
        print(f"Filtered books: {filtered_books}")

        if not filtered_books:
            results = [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="No results found",
                    input_message_content=InputTextMessageContent(
                        "No books match your search."
                    ),
                ),
            ]
        else:

            results = [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=book.title,
                    description="Description: "
                                "Lorem ipsum dolor sit amet, consectetuer",
                    input_message_content=InputTextMessageContent(
                        f"Book: {book.title}\n"
                        f"Author: {book.author}\n"
                        "Description: Lorem ipsum dolor sit amet, consectetuer"
                    ),
                )
                for book in filtered_books
            ]

        await inline_query.answer(results)
