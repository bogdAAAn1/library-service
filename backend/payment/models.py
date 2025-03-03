from django.db import models


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"

    class PaymentType(models.TextChoices):
        PAYMENT = "payment", "Payment"
        FINE = "fine", "Fine"

    status = models.CharField(
        max_length=7, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    type = models.CharField(
        max_length=7, choices=PaymentType.choices, default=PaymentType.PAYMENT
    )
    borrowing = models.ForeignKey(
        "borrowing.Borrowing", related_name="payments", on_delete=models.CASCADE
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            f"Payment {self.id} for Borrowing {self.borrowing_id}: "
            f"{self.type} - {self.status} ({self.money_to_pay} USD)"
        )
