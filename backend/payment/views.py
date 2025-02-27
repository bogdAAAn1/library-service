from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer


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

        if user.is_stuff:
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


@api_view(["GET"])
def payment_success_view(request):
    pass # TODO check successful stripe payment


@api_view(["GET"])
def payment_cancel_view(request):
    pass # TODO return payment paused message (just message)
