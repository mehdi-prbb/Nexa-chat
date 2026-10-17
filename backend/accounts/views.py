from rest_framework import generics

from .serializers import UserCreateSerializer
from rest_framework.permissions import AllowAny


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    