from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.Serializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )


class PaymentDetailSerializer(PaymentSerializer):
    pass # TODO nested serializer for borrowing field
