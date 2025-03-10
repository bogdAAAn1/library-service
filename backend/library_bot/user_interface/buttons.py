from telegram import InlineKeyboardButton, InlineKeyboardMarkup


(
    START_ROUTES,
    BOOKS,
    MY_BORROWINGS,
    ACTIVE_BORROW,
    ARCHIVE,
    FAQ,
    RANDOM_BOOK) = range(7)


async def send_back_button(query) -> None:
    keyboard = [
        [InlineKeyboardButton("◀️ Back", callback_data="WELCOME_POST")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(
        text="Press the button below to go back.", reply_markup=reply_markup
    )

    return START_ROUTES
