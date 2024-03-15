from accounts.models import User, UserHistory, ContactUs

from rest_framework.serializers import (
    ModelSerializer,
)

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email',
        ]
        extra_kwargs = {
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_superuser': {'read_only': True},
            'is_email_verified': {'read_only': True},
            # 'role': {'read_only': True},
        }


class CustomRegisterSerializer(RegisterSerializer):
    full_name = serializers.CharField(required=True)
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    
    def save(self, request):
        user = super(CustomRegisterSerializer, self).save(request)
        user.full_name = self.validated_data.get('full_name', '')
        user.save()
        return user


class UserHistorySerializer(ModelSerializer):
    class Meta:
        model = UserHistory
        fields = [
            'user', 'image', 'date', 'classification', 'confidence', 'description', 'solution',
        ]


class ContactUsSerializer(ModelSerializer):
    class Meta:
        model = ContactUs
        fields = [
            'name', 'phone', 'email', 'message', 'date'
        ]