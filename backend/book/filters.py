import django_filters
from django.db.models import Q

from book.models import Book


class BookFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(method="search_by_ids")
    author = django_filters.CharFilter(method="search_by_authors")

    daily_fee = django_filters.NumberFilter(
        field_name="daily_fee"
    )  # /api/books/?daily_fee=15.50

    min_fee = django_filters.NumberFilter(
        field_name="daily_fee", lookup_expr="gte"
    )  # /api/books/?min_fee=10&max_fee=20
    max_fee = django_filters.NumberFilter(field_name="daily_fee", lookup_expr="lte")

    class Meta:
        model = Book
        fields = ["id", "author", "daily_fee", "min_fee", "max_fee"]

    def search_by_ids(self, queryset, name, value):
        if not value:
            return queryset
        ids_list = value.split(",")
        return queryset.filter(id__in=ids_list).distinct()

    def search_by_authors(self, queryset, name, value):
        if not value:
            return queryset
        authors_list = value.split(",")
        query = Q()
        for search_author in authors_list:
            query |= Q(author__icontains=search_author)
        return queryset.filter(query).distinct()
