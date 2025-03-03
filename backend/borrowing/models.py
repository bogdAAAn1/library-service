from datetime import datetime

from django.conf import settings
from django.db import models

from book.models import Book
from payment.models import Payment


FINE_MULTIPLIER = 2


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    def get_payment_type(self, date_now: datetime.date):
        """return payment type"""
        if date_now > self.expected_return_date:
            return Payment.PaymentType.FINE
        return Payment.PaymentType.PAYMENT

    def get_payment_message(self, date_now: datetime.date):
        """return payment message"""
        if self.get_payment_type(date_now) == Payment.PaymentType.FINE:
            return "The book is returned overdue. You need to pay a fine."
        return "The book is returned on time. Please pay the rental fee."

    def get_total_rental_fee(self, date_now: datetime.date):
        """return total rental fee"""
        if date_now and self.borrow_date:
            rental_days = (date_now - self.borrow_date).days
            return max(rental_days, 1) * self.book.daily_fee
        return self.book.daily_fee

    def get_late_fee(self, date_now: datetime.date):
        """return late fee"""
        if self.actual_return_date and self.expected_return_date:
            if date_now > self.expected_return_date:
                overdue_days = (date_now - self.expected_return_date).days
                return overdue_days * self.book.daily_fee * FINE_MULTIPLIER
        return 0

    def get_total_payment(self, date_now: datetime.date):
        """return total payment"""
        rental_fee = self.get_total_rental_fee(date_now)
        late_fee = self.get_late_fee(date_now)
        return rental_fee + late_fee

    def __str__(self) -> str:
        return (
            f"Borrowing by {self.user} - "
            f"Book: {self.book.title} on {self.borrow_date}"
        )
