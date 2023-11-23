"""
Views for the user API
"""
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import (
    status,
    generics
)
from rest_framework_simplejwt import authentication as authenticationJWT
from datetime import timedelta
from django.utils import timezone
from user.serializers import UserSerializer
from .permissions import IsCreationOrIsAuthenticated


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class ManagerUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [
        authenticationJWT.JWTAuthentication]
    permission_classes = [IsCreationOrIsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        user = self.request.user
        created_time = user.created_at
        current_time = timezone.now()

        if (current_time >= created_time + timedelta(minutes=3)) and user.status != "Aprovado":
            user.status = "Aprovado"
            user.save()

        return user

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to user."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
