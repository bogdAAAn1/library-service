from rest_framework import serializers

from borrowing.models import Borrowing
from book.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.book.inventory == 0:
            return None
        return data


class BorrowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "book")


class BorrowingRetrieveSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_return_date", "actual_return_date", "book")


