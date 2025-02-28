from rest_framework import serializers

from borrowing.models import Borrowing
from book.serializers import BookSerializer
from payment.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")

    def validate(self, attrs):
        if attrs["book"].inventory < 1:
            raise serializers.ValidationError("This book is not available")

        return attrs


class BorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "book")


class BorrowingRetrieveSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book")


class BorrowingReturnSerializer(BorrowingRetrieveSerializer):
    payments = PaymentSerializer(many=False, read_only=True)
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book", "payments")


