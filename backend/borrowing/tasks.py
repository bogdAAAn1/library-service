import asyncio
import os
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages.constants import SUCCESS
from django.core.mail import EmailMessage
from dotenv import load_dotenv
from telegram import Bot

from borrowing.models import Borrowing
from borrowing.views import export_borrows_to_excel

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
sum_of_all_borrows = Borrowing.objects.count()
sum_of_overdue_borrows = Borrowing.objects.filter(
    expected_return_date__lt=datetime.now()
).count()


@shared_task
def morning_borrow_update():
    if sum_of_all_borrows > 0:
        message = (
            f"Today we have {sum_of_all_borrows} borrowings.\n\n"
            f"Total overdue {sum_of_overdue_borrows} books.\n\n"
            "Details report was send on corporate email."
        )
    else:
        message = "Today we have no borrowings."

    async def send():
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)

    asyncio.run(send())
    return "Success"


@shared_task
def send_borrows_to_email():
    detailed_borrows_document = export_borrows_to_excel()
    email = EmailMessage(
        subject=f"Borrowing-daily-report-"
                f"{datetime.now().strftime('%Y-%m-%d')}",
        body="Dear colleagues.\n"
        "Attached you will find the daily borrowing report for today.\n"
        "Here are the key details:\n"
        f"Total number of borrowings: {sum_of_all_borrows}.\n"
        f"Number of overdue borrowings: {sum_of_overdue_borrows}\n"
        "This report includes all relevant data regarding borrowings,\n"
        "including borrow date, "
        "expected return date, and actual return date.\n"
        "If you have any questions or need further information,\n"
        "please don't hesitate to reach out.",
        from_email=settings.EMAIL_HOST_USER,
        to=[settings.RECIPIENT_ADDRESS],
    )

    email.attach(
        f"borrowing-daily-report-{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        detailed_borrows_document.read(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    email.send()
    return "Success"


@shared_task
def send_notification_to_telegram(message):
    async def send():
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)

    asyncio.run(send())


@shared_task
def send_user_almost_overdue_borrowing_notification():
    User = get_user_model()
    user_ids = [user.tg_chat for user in User.objects.all()]
    one_day_ahead_expected_return_date = datetime.now() + timedelta(days=1)

    for user_id in user_ids:
        borrowings = Borrowing.objects.filter(
            expected_return_date__lte=one_day_ahead_expected_return_date,
            expected_return_date__gt=datetime.now(),
            user__tg_chat=user_id,
        ).select_related("book")

        for borrow in borrowings:
            message = (
                f"Borrow need to be returned:\n\n"
                f"Book: {borrow.book.title}\n"
                f"Author: {borrow.book.author}\n\n"
                f"Borrow date: {borrow.borrow_date}\n"
                f"Expected return date: {borrow.expected_return_date}\n"
            )

    async def send():
        bot = Bot(token=token)
        for user_id in user_ids:
            await bot.send_message(chat_id=user_id, text=message)

    asyncio.run(send())

    return "Success"
