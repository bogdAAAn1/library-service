import stripe
from django.conf import settings
from django.urls import reverse

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, request, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing: Borrowing, request) -> Payment:
    total_price = int(borrowing.book.daily_fee * 100)

    success_url = request.build_absolute_uri(reverse("payment:payment-success")) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payment:payment-cancel"))

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": borrowing.book.title
                },
                "unit_amount": total_price,
            },
            "quantity": 1
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        status=Payment.PaymentStatus.PENDING,
        type=Payment.PaymentType.PAYMENT,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=borrowing.book.daily_fee
    )

    return payment


@extend_schema(tags=["payments"])
class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Payment.objects.select_related()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Payment.objects.select_related()
        return (
            Payment.objects.
            select_related().
            filter(borrowing_id__user=user)
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return self.serializer_class


@extend_schema(tags=["payments"])
@api_view(["GET"])
def payment_success_view(request):
    session_id = request.GET.get("session_id")
    payment = get_object_or_404(Payment, session_id=session_id)

    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        payment.status = Payment.PaymentStatus.PAID
        payment.save()
        return Response({"message": "success"}, status=status.HTTP_200_OK)

    return Response({"error": "error"}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["payments"])
@api_view(["GET"])
def payment_cancel_view(request):
    return Response({"message": "Payment was cancelled"}, status=status.HTTP_400_BAD_REQUEST)
