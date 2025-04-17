from django.urls import path
from .views import add_comment
from . import views

urlpatterns = [
    path('', views.home, name='home'),  
    path('createPost/', views.createPost, name='createPost'), 
    path('add_comment/<int:post_id>/', add_comment, name='add_comment'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),

]

