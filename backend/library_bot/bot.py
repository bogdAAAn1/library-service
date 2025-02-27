import os
import sys
import django

from dotenv import load_dotenv
from django.contrib.auth import get_user_model

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")

django.setup()

User = get_user_model()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



async def start(update: Update, context: CallbackContext) -> None:
    user_telegram_id = update.message.chat_id

    await update.message.reply_text("Welcome to the library")



def main():
    load_dotenv()
    app = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()


if __name__ == "__main__":
    main()