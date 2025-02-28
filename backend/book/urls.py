from django.urls import path, include
from rest_framework import routers

from book.views import BookViewSet

app_name = "book"

router = routers.DefaultRouter(trailing_slash=False)
router.register("", BookViewSet)

urlpatterns = [path("", include(router.urls))]
