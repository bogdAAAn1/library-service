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
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings"
    )

    def get_payment_type(self):
        """return payment type"""
        if self.actual_return_date and self.actual_return_date > self.expected_return_date:
            return Payment.PaymentType.FINE
        return Payment.PaymentType.PAYMENT

    def get_payment_message(self):
        """return payment message"""
        if self.get_payment_type() == Payment.PaymentType.FINE:
            return "The book is returned overdue. You need to pay a fine."
        return "The book is returned on time. Please pay the rental fee."

    def get_total_rental_fee(self):
        """return total rental fee"""
        if self.actual_return_date and self.borrow_date:
            rental_days = (self.actual_return_date - self.borrow_date).days
            return max(rental_days, 1) * self.book.daily_fee
        return self.book.daily_fee

    def get_late_fee(self):
        """return late fee"""
        if self.actual_return_date and self.expected_return_date:
            if self.actual_return_date > self.expected_return_date:
                overdue_days = (self.actual_return_date - self.expected_return_date).days
                return overdue_days * self.book.daily_fee * FINE_MULTIPLIER
        return 0

    def get_total_payment(self):
        """return total payment"""
        rental_fee = self.get_total_rental_fee()
        late_fee = self.get_late_fee()
        return rental_fee + late_fee

    def __str__(self) -> str:
        return f"Borrowing by {self.user} - Book: {self.book.title} on {self.borrow_date}"
