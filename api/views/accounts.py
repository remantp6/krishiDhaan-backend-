import re
import random

from accounts.models import User
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAdminUser
from rest_framework.viewsets import ViewSet, ModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from django.core.mail import send_mail
from django.conf import settings

from api.serializers.accounts import (
    UserSerializer,
)
from allauth.socialaccount.models import SocialAccount

from api.utils import send_otp

class SentOtpViewSet(ViewSet):
    def dispatch(self, request, *args, **kwargs):
        self.payload = {}
        return super().dispatch(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        sa = SocialAccount.objects.filter(user__email=request.data.get('email'))
        if not sa.exists():
            user, created = User.objects.get_or_create(
                email=request.data.get('email'),
            )
            if User.objects.filter(email=request.data.get('email')).exists():
                serializer = UserSerializer(data=request.data, instance=user)
            else:
                serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # generate otp
            otp = str(random.randint(000000, 999999))
            # ensure that otp is 6 digits
            if len(otp) < 6:
                otp = otp.zfill(6)
            user.set_password(otp)
            user.save()

            # send otp to user
            send_otp(user.email, otp)

            self.payload['otp'] = otp
            self.payload['message'] = 'OTP sent successfully'
            if created:
                self.payload['is_signup'] = True
                return Response(self.payload, status=status.HTTP_201_CREATED)
            else:
                self.payload['is_signup'] = False
                return Response(self.payload, status=status.HTTP_200_OK)
        else:
            self.payload['error'] = f'User already exists. Please login with {sa.first().provider} account'
            return Response(self.payload, status=status.HTTP_400_BAD_REQUEST)
            

class UserLoginSignUpViewSet(ViewSet):
    def dispatch(self, request, *args, **kwargs):
        self.payload = {}
        return super().dispatch(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user = User.objects.filter(
            email=request.data.get('email'),
        ).first()
        # check otp
        if user.check_password(request.data.get('otp')):
            # generate token
            token, created = Token.objects.get_or_create(user=user)
            self.payload['token'] = token.key
            self.payload['profile'] = UserSerializer(user).data
            return Response(self.payload, status=status.HTTP_200_OK)
        else:
            self.payload['error'] = 'Invalid OTP'
            return Response(self.payload, status=status.HTTP_400_BAD_REQUEST)

class UserProfileViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'put', 'patch']

    def dispatch(self, request, *args, **kwargs):
        self.payload = {
            'profile': {},
            # 'data': {}
        }
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id).first()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset)
        self.payload['profile'] = serializer.data
        return Response(self.payload, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.payload['profile'] = serializer.data
        return Response(self.payload, status=status.HTTP_200_OK)