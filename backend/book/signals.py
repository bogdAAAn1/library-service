from django.db.models.signals import post_save
from django.dispatch import receiver

from book.models import Book
from book.tasks import new_book_available_notification


@receiver(post_save, sender=Book)
def new_book_available(sender, instance, created, **kwargs):
    if created:
        message = (
            f"We have a new book:\n\n"
            f"Book: {instance.title}\n"
            f"Author: {instance.author}\n\n"
            "Description: Lorem ipsum dolor sit amet, consectetuer"
        )
        new_book_available_notification.delay(message)