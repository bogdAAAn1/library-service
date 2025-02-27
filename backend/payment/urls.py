from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import (
    payment_success_view,
    payment_cancel_view,
    PaymentViewSet
)

app_name = "payment"

router = DefaultRouter()
router.register("payment", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("success/", payment_success_view, name="payment-success"),
    path("cancel/", payment_cancel_view, name="payment-cancel")
]
