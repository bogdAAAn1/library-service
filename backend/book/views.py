from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from book.models import Book


class BookViewSet(
    mixins.CreateModelMixin,
   mixins.RetrieveModelMixin,
   mixins.UpdateModelMixin,
   mixins.DestroyModelMixin,
   mixins.ListModelMixin,
   GenericViewSet
):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
