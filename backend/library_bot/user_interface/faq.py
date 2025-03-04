from telegram import Update
from telegram.ext import CallbackContext

from library_bot.user_interface.buttons import send_back_button

async def get_faq(update: Update, context: CallbackContext) -> None:
    """
    Handles the FAQ section for the user. It sends a message containing frequently asked questions
    with answers.
    """
    await update.callback_query.message.reply_text(
        "1. *How can I borrow books?*\n"
        "You can borrow books by searching for the title or author in the bot. "
        "Once you find the book you're interested in, you can manually visit the library "
        "or follow the instructions provided to borrow it.\n\n"

        "2. *How do I return borrowed books?*\n"
        "To return a book, simply visit the library and return it directly. "
        "You can also check your borrowed books list in the bot to keep track of your "
        "due dates and return reminders.\n\n"

        "3. *How do I check the status of my borrowed books?*\n"
        "You can check the status of your borrowed books in the 'My Borrowings' "
        "section. It will show you the borrowing date, expected return date, "
        "and whether the book is overdue.\n\n"

        "4. *What should I do if I can't find a book in the bot?*\n"
        "If the book you're looking for isn't available, "
        "you can either try searching again later or contact our support team for assistance.\n\n"

        "5. *How is the overdue fee calculated?*\n"
        "The overdue fee is calculated for each day the book is overdue. "
        "If you have any questions about the fee, feel free to contact our support team.\n",

        parse_mode="MARKDOWN"
    )

    await send_back_button(update.callback_query)
