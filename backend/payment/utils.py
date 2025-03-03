from datetime import datetime

import stripe
from django.conf import settings
from django.db import transaction
from django.urls import reverse

from borrowing.models import Borrowing
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@transaction.atomic
def create_stripe_session(
    borrowing: Borrowing, request, date_now: datetime.date
) -> Payment:
    payment_type = borrowing.get_payment_type(date_now)
    total_payment = borrowing.get_total_payment(date_now)
    total_price = int(total_payment * 100)

    success_url = (
        request.build_absolute_uri(reverse("payment:payment-success"))
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = request.build_absolute_uri(reverse("payment:payment-cancel"))

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{borrowing.book.title} "
                                f"({payment_type}: {total_payment}$)"
                    },
                    "unit_amount": total_price,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        status=Payment.PaymentStatus.PENDING,
        type=payment_type,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=total_payment,
    )

    return payment
