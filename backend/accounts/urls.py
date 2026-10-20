from django.urls import path

from .views import UserCreateView, UserView


urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('profile/', UserView.as_view(), name='profile')
]
