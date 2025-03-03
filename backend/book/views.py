from typing import List

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from book.filters import BookFilter
from book.models import Book
from book.serializers import BookSerializer, BookImageSerializer
from schemas.book_schema_decorator import book_schema_view


@extend_schema(tags=["book"])
@book_schema_view()
class BookViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "cover", "inventory"]
    filterset_class = BookFilter
    ordering_fields = ["id", "title", "author", "inventory", "daily_fee"]
    ordering = ["id"]
    permission_classes = [IsAdminUser]

    def get_permissions(self) -> List[BasePermission]:
        if self.action in ["list", "retrieve"]:
            return []
        return [permission() for permission in self.permission_classes]
