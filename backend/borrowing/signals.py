from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowing.models import Borrowing
from borrowing.tasks import send_notification_to_telegram
from payment.models import Payment


@receiver(post_save, sender=Borrowing)
def send_borrow_creation(sender, instance, created, **kwargs):
    if created:

        message = (f"New borrowing created:\n"
                   "--------------\n"
                   f"User: {instance.user.first_name} {instance.user.last_name}\n"
                   "--------------\n"
                   f"Book: {instance.book.title}\n"
                   f"Author: {instance.book.author}\n"
                   "--------------\n"
                   f"Borrowing date: {instance.borrow_date}\n"
                   f"Returned date: {instance.expected_return_date}"
                   )
        send_notification_to_telegram.delay(message)


def change_borrowing_status(instance):
    instance.actual_return_date = datetime.now().date()
    instance.save()
    book = instance.book
    book.inventory += 1
    book.save()


@receiver(post_save, sender=Payment)
def borrowing_paid(sender, instance, created, **kwargs):
    if not created and instance.status == "paid":
            print("change status")
            borrowing = instance.borrowing
            change_borrowing_status(borrowing)
