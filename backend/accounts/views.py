from rest_framework import generics

from .serializers import UserCreateSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


class UserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user