from django.urls import path

from borrowing.views import (
    borrowing_list,
    borrowing_detail,
    borrowing_return
)

urlpatterns = [
    path("borrowings/", borrowing_list, name="borrowings-list"),
    path("borrowings/<int:pk>/", borrowing_detail, name="borrowings-detail"),
    path("borrowing/<int:pk>/return/", borrowing_return, name="borrowings-return"),
]