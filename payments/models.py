from django.db import models
import stripe
import posts

def Order():
    stripe.Order.create(
    currency="usd",
    email="student@mocs.flsouthern.edu",
    items=[
        {
        "post id": "post.id",
        "title": "post.title",
        "price": "post.price"
        },
    ],
    shipping={
        "name": "Mocsie Rogers",
        "housing": "Spivey",
    },
)