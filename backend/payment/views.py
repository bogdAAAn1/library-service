import stripe

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payment.models import Payment
from payment.serializers import PaymentSerializer


@extend_schema(tags=["payments"])
@payment_schema_view()
class PaymentViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Payment.objects.select_related()
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Payment.objects.select_related()
        return Payment.objects.select_related().filter(borrowing_id__user=user)


@payment_success_view_schema()
@api_view(["GET"])
def payment_success_view(request):
    session_id = request.GET.get("session_id")
    payment = get_object_or_404(Payment, session_id=session_id)

    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        payment.status = Payment.PaymentStatus.PAID
        payment.save()
        return Response({"message": "Payment successful!"}, status=status.HTTP_200_OK)

    return Response({"error": "Payment failed!"}, status=status.HTTP_400_BAD_REQUEST)


@payment_chancel_view_schema()
@api_view(["GET"])
def payment_cancel_view(request):
    return Response({"message": "Payment was cancelled!"}, status=status.HTTP_400_BAD_REQUEST)
