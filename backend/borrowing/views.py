from django.db.models import QuerySet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer


def _filtering_borrowing_list(borrowings: QuerySet, is_active: str) -> QuerySet:
    if is_active == "true":
        borrowings = borrowings.filter(actual_return_date__isnull=True)
    if is_active == "false":
        borrowings = borrowings.filter(actual_return_date__isnull=False)

    return borrowings


@api_view(["GET", "POST"])
def borrowing_list(request):
    if request.method == "GET":
        borrowing = Borrowing.objects.all()
        user_id = request.GET.get("user_id")
        is_active = request.GET.get("is_active")
        if request.user.is_staff:
            if user_id:
                borrowing = borrowing.filter(user__id=user_id)
            if is_active:
                borrowing = _filtering_borrowing_list(borrowing, is_active)

        else:
            borrowing = borrowing.filter(user__id=request.user.id)
            if is_active:
                borrowing = _filtering_borrowing_list(borrowing, is_active)

        serializer = BorrowingListSerializer(borrowing, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    if request.method == "POST":
        serializer = BorrowingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        serializer.data.get("book").inventory -= 1
        return Response(serializer.data, status=HTTP_201_CREATED)
