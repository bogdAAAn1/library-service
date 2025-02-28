from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.db.models import QuerySet
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingRetrieveSerializer


def _filtering_borrowing_list(borrowings: QuerySet, is_active: str) -> QuerySet:
    if is_active == "true":
        borrowings = borrowings.filter(actual_return_date__isnull=True)
    if is_active == "false":
        borrowings = borrowings.filter(actual_return_date__isnull=False)

    return borrowings


@api_view(["GET", "POST"])
@permission_required([IsAdminUser])
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

@api_view(["GET"])
def borrowing_detail(request, pk):
    borrowing = Borrowing.objects.get(pk=pk)
    serializer = BorrowingRetrieveSerializer(borrowing)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(["POST"])
def borrowing_return(request, pk):
    borrowing = Borrowing.objects.get(pk=pk)
    if borrowing.actual_return_date is None:
        borrowing.actual_return_date = datetime.now()
        borrowing.book.inventory += 1
        borrowing.save()
        return Response(status=HTTP_200_OK)
    else:
        return Response(status=HTTP_404_NOT_FOUND)
