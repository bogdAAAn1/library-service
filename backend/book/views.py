from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser
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

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "cover", "inventory"]
    filterset_class = BookFilter
    ordering_fields = ["title", "author", "inventory", "daily_fee"]
    ordering = ["id"]

    def get_serializer_class(self):

        if self.action == "upload_image":
            return BookImageSerializer

        return BookSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image of cover to book"""
        book = self.get_object()
        serializer = self.get_serializer(book, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @book_filter_schema()
    # def list(selfself, request, *args, **kwargs):
    #     """
    #     Return filtered list if query parameters exist, else - full list of items
    #     """
