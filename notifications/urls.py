from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('list/', views.notifications_list, name='notifications_list'),
    path('send-dm/<int:recipient_id>/', views.send_dm_notification, name='send_dm'),
    path('send-post/<int:post_id>/', views.send_post_notification, name='send_post'),
    path('mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_as_read'),
    path('mark-all-as-read/', views.mark_all_read, name='mark_all_as_read'),
    path('buy/<int:post_id>/', views.buy_post, name='buy_post'),
]