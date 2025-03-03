from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from library_bot.user_interface.stages import *


async def send_back_button(query) -> None:
    """
    Sends a "Back" button to the user, allowing them to navigate back to the welcome screen.
    The message includes instructions to press the button below.
    """
    keyboard = [
        [InlineKeyboardButton("◀️ Back", callback_data="WELCOME_POST")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        text="Press the button below to go back.", reply_markup=reply_markup
    )

    return START_ROUTES
