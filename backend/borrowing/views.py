from datetime import datetime
from http.client import responses
from io import BytesIO

import pandas as pd
from django.contrib.auth.decorators import permission_required
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import F

from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST
)

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingRetrieveSerializer,
    BorrowingReturnSerializer
)
from payment.views import create_stripe_session


def _filtering_borrowing_list(borrowings: QuerySet, is_active: str) -> QuerySet:
    if is_active == "true":
        borrowings = borrowings.filter(actual_return_date__isnull=True)
    if is_active == "false":
        borrowings = borrowings.filter(actual_return_date__isnull=False)

    return borrowings


@api_view(["GET", "POST"])
@permission_required([IsAuthenticated])
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
        borrowing = serializer.save(user=request.user)

        book = Book.objects.get(id=serializer.data.get("book"))
        book.inventory -= 1
        book.save()

        payment = create_stripe_session(borrowing, request)

        response_data = serializer.data
        response_data["payment_url"] = payment.session_url
        response_data["payment_status"] = payment.status

        return Response(response_data, status=HTTP_201_CREATED)

@api_view(["GET"])
@permission_required([IsAuthenticated])
def borrowing_detail(request, pk):
    borrowing = Borrowing.objects.get(pk=pk)
    serializer = BorrowingRetrieveSerializer(borrowing)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(["POST"])
@permission_required([IsAuthenticated])
def borrowing_return(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)

    if borrowing.actual_return_date is None:
        borrowing.actual_return_date = datetime.now().date()

        book = borrowing.book
        book.inventory += 1
        book.save()

        borrowing.save()
        return Response(BorrowingReturnSerializer(borrowing).data, status=HTTP_200_OK)
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


