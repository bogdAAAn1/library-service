import logging
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

from library_bot.user_interface.stages import *

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def show_book_search_hint(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """This function handles the callback query for the 'BOOKS' button.
    It provides a hint to the user on how to search for books
    and includes a 'Back' button to return to the previous menu.

    When the user clicks the 'BOOKS' button:
    1. The callback query is answered.
    2. A message is sent with instructions on how to search for books by title.
    3. A 'Back' button is displayed to return to the previous menu."""

    query = update.callback_query
    logger.info("BOOK button clicked")
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
    """This function retrieves all books from the database asynchronously.
    It uses `sync_to_async` to execute a synchronous database query in an asynchronous context.
    Returns a list of all books in the form of a Python list."""

    return await sync_to_async(lambda: list(Book.objects.all()))()


async def inline_book_search(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """The function handles inline search queries made by the user through the Telegram bot.
    It performs the following tasks:

    Checks for an inline query:
    It checks if the update contains an inline query (update.inline_query).
    Inline queries are used when users type the bot's username and a query in the text field of Telegram.
    Extracts the search query: If the inline query exists, it retrieves the search
    query from the inline query object (inline_query.query).

    Processes the query:

    If the query is empty, the function returns without performing any search.
    If the query contains text, it proceeds to fetch all books from the database using await get_books().

    Filters books based on the query:
    It filters the list of books to match the title with the search query (case-insensitive).
    The filtered list (filtered_books) is then checked to see if it contains any books.
    f no books match, a message stating "No books match your search" is shown to the user.
    Prepares results:
    If matching books are found, it creates a list of InlineQueryResultArticle objects,
    which will be sent back as results of the inline query. Each InlineQueryResultArticle contains the
    title of the book and its author.

    Sends the results back:
    Finally, the function calls inline_query.answer(results) to send the filtered results back to the user.
    """

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
                    description="Description: Lorem ipsum dolor sit amet, consectetuer",
                    input_message_content=InputTextMessageContent(
                        f"Book: {book.title}\n"
                        f"Author: {book.author}\n"
                        "Description: Lorem ipsum dolor sit amet, consectetuer"
                    ),
                )
                for book in filtered_books
            ]

        await inline_query.answer(results)
