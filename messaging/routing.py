from django.urls import re_path
from . import consumers  # Replace with your consumers import path

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<current_user>\w+)/(?P<target_user>\w+)/$', consumers.MessagingConsumer.as_asgi()),
]