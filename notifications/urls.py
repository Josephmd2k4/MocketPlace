from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('send-dm/<int:recipient_id>/', views.send_dm_notification, name='send_dm'),
    path('send-post/<int:post_id>/', views.send_post_notification, name='send_post'),
    path('list/', views.notification_list, name='list'),
]