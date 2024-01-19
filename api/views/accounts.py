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
    UserSerializer, User3StepFormSerializer, UserActiveDeactiveSerializer
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


class User3stepFormViewset(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = User3StepFormSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['patch']

    def dispatch(self, request, *args, **kwargs):
        self.payload = {
            'profile': {},
        }
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id).first()

    def patch(self, request, *args, **kwargs):
        data = request.data.copy()
        data['is_signup'] = False
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.payload['profile'] = serializer.data
        if(serializer.data['first_name']):
            name = "Name: " + serializer.data['first_name']  + " " + serializer.data['last_name'] + "\n"
        else:
            name = ""
        # send email to email
        try:
            message_body = "New user registered with details: \n\n" + name + \
                "Email: " + serializer.data['email'] + "\n" + \
                "User Role: " + re.sub(r'[\[\]"\']', '', serializer.data['user_role']) or "" + "\n" + \
                "Need To Make: " + re.sub(r'[\[\]"\']', '', serializer.data['need_to_make']) or "" + "\n" + \
                "Heard About Us In: " + re.sub(r'[\[\]"\']', '', serializer.data['hear_about_us']) or "" + "\n" 
            send_mail("New User Registered", message_body, settings.DEFAULT_FROM_EMAIL,  [settings.ADMIN_MAIL, 'bimalsubedi04@gmail.com'], fail_silently=True)
        except Exception as e:
            print(f'Error while sending mail: {e}')
            pass
        return Response(self.payload, status=status.HTTP_200_OK)


class UsersListViewSet(ModelViewSet):
    queryset = User.objects.filter(is_superuser=False, role__in=['U', 'B'])
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminUser, )
    http_method_names = ['get']

    def dispatch(self, request, *args, **kwargs):
        self.payload = {
            'profiles': {},
        }
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.queryset.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        self.payload['users'] = serializer.data
        return Response(self.payload, status=status.HTTP_200_OK)


class UserActiveDeactiveViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserActiveDeactiveSerializer
    permission_classes = (IsAuthenticated, IsAdminUser, )
    http_method_names = ['patch']

    def dispatch(self, request, *args, **kwargs):
        self.payload = {
            'profile': {},
        }
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.queryset.filter(id=self.request.GET.get('user_id', 0)).first()

    def patch(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        self.payload['profile'] = serializer.data
        return Response(self.payload, status=status.HTTP_200_OK)