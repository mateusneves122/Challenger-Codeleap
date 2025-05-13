from django.urls import path
from . import views

urlpatterns = [
    path('users/<int:user_id>/follow/', views.follow_user, name='follow_user'),
    path('users/<int:user_id>/unfollow/', views.unfollow_user, name='unfollow_user')
]