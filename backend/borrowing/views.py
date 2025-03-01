from datetime import datetime
from io import BytesIO

import pandas as pd
from django.contrib.auth.decorators import permission_required
from django.db.models import QuerySet
from django.http import HttpResponse
from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingRetrieveSerializer


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
        book = Book.objects.get(id=serializer.data.get("book"))
        book.inventory -= 1
        book.save()
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

def export_borrows_to_excel():
    borrowings = Borrowing.objects.select_related("book", "user").values(
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
    ).annotate(
        borrow_id=F("id"),
        title=F("book__title"),
        first_name=F("user__first_name"),
    )

    df = pd.DataFrame(list(borrowings))

    file_buffer = BytesIO()
    df.to_excel(file_buffer, index=False, engine='openpyxl')
    file_buffer.seek(0)

    return file_buffer

def get_overdue_borrowings():
    return Borrowing.objects.filter(expected_return_date__lt=datetime.now())