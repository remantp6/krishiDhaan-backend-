from accounts.models import User

from rest_framework.serializers import (
    ModelSerializer,
)

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'role'
        ]
        extra_kwargs = {
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
            'is_email_verified': {'read_only': True},
            'role': {'read_only': True},
        }

class User3StepFormSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'user_role', 'need_to_make', 'hear_about_us', 'is_signup']
        read_only_fields = ['user', 'first_name', 'last_name', 'email']


class UserActiveDeactiveSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'user_role']
