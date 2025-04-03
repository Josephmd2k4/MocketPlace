from django.urls import path
from .views import send_friend_request, accept_friend_request, reject_friend_request, list_friends

app_name = 'friends'

urlpatterns = [
    path('send/<int:receiver_id>/', send_friend_request, name='send_friend_request'),
    path('accept/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('reject/<int:request_id>/', reject_friend_request, name='reject_friend_request'),
    path('list/', list_friends, name='list_friends'),
]
