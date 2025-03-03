from datetime import datetime

from rest_framework import serializers

from borrowing.models import Borrowing
from book.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")

    def validate(self, attrs):
        if attrs["book"].inventory < 1:
            raise serializers.ValidationError("This book is not available")

        if attrs["expected_return_date"] < datetime.now().date():
            raise serializers.ValidationError("Invalid return date")

        return attrs


class BorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "book")


class BorrowingRetrieveSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
