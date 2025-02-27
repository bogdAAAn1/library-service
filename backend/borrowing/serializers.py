from rest_framework import serializers

from borrowing.models import Borrowing


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
        fields = ("id", "borrow_date", "actual_return_date", "expected_return_date", "book")


