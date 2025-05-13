from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.post_user, name='post_user'),
    path('users/<int:user_id>/', views.user_detail_operations, name='user_detail_operations')
]