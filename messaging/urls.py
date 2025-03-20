from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Add your regular views here
    path('chat/<str:target_user>/', views.dm_view, name='dm'),
]
