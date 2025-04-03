from django.urls import path
from .views import transact_status_view, create_new_payout

urlpatterns = [
    path("checkout/", create_new_payout, name="paypal_checkout"),
    path("status/", transact_status_view, name="transaction_status")
]
