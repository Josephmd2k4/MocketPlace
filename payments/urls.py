from django.urls import path
from . import views

urlpatterns = [
    path("checkout/", views.create_new_payout, name="general_checkout"),
    path("status/", views.transact_status_view, name="transaction_status"),
    path("paypal/", views.paypal_webhook, name="paypal_webhook"),
    path("form/", views.payout_form, name="payout_form"),
]
