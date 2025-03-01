from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

# Stages
START_ROUTES, MY_BORROWINGS, BOOKS, PAY_BORROW, FAQ, ACTIVE_BORROW, ARCHIVE = range(7)


async def send_back_button(query) -> None:
    keyboard = [[InlineKeyboardButton("Back", callback_data="WELCOME_POST")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        text="Press the button below to go back.",
        reply_markup=reply_markup
    )

    return START_ROUTES