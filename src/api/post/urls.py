
from django.urls import path
from . import views

urlpatterns = [
   path('posts/', views.create_post, name='create_post'),
   path('users/<int:user_id>/posts/', views.list_user_posts, name='list_user_posts'),
   path('posts/<int:post_id>/', views.post_detail_operations, name='post_detail_operations')
]