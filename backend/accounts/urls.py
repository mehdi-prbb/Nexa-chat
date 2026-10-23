from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserCreateView, UserView, LoginView


urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('profile/', UserView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('token_refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
