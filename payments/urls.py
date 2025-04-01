from django.urls import path
from .views import paypal_webhook, payout_status_view

urlpatterns = [
    path("webhook/paypal/", paypal_webhook, name="paypal_webhook"),
    path("payouts/status/", payout_status_view, name="payout_status")
]
