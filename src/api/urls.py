from django.urls import path, include

urlpatterns = [
    path('', include('api.user.urls')),
    path('', include('api.post.urls')),
    path('', include('api.auth.urls')),
    path('', include('api.social.urls'))
]