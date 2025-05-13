from django.urls import path
from . import views

urlpatterns = [
    path('auth/token/', views.post_auth, name='post_auth')
]