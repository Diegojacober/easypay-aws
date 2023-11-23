"""
Serializers for the user API View.
"""
from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers

from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name',
                  'last_name', 'cpf', 'url_image', 'status', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5},
            'is_active': {'read_only': True},
            'status': {'read_only': True},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
