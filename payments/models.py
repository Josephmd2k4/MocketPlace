from django.db import models
import stripe

def Order():
    stripe.Order.create(
    currency="usd",
    email="jenny.rosen@example.com",
    items=[
        {
        "type": "sku",
        "parent": "sku_xxxxxxxxxxxxx",
        },
    ],
    shipping={
        "name": "Jenny Rosen",
        "address": {
        "line1": "1234 Main Street",
        "city": "San Francisco",
        "state": "CA",
        "country": "US",
        "postal_code": "94111",
        },
    },
)