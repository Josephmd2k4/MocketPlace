from django.urls import path, include
from . import views
from posts.models import Post

urlpatterns = [
    path('payment/<int:post_id>/<path:media_file>', views.payment_view, name='payment_view'),
]
