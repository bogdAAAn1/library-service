from django.urls import path

from borrowing.views import (
    borrowing_list,
    borrowing_detail,
    borrowing_return,
)

urlpatterns = [
    path("", borrowing_list, name="borrowings-list"),
    path("<int:pk>/", borrowing_detail, name="borrowings-detail"),
    path("return/", borrowing_return, name="borrowings-return"),
]

app_name = "borrowing"
