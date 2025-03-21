from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'messaging'

urlpatterns = [
    # Add your regular views here
    path('chat/<str:target_user>/', views.dm_view, name='dm'),
    path('upload/', views.upload_view, name='upload_view'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
