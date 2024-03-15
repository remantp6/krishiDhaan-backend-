from accounts.models import User, UserHistory, ContactUs
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from api.serializers.accounts import (
    UserSerializer, UserHistorySerializer, ContactUsSerializer
)

from django.core.mail import send_mail
from django.conf import settings


class UserProfileViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'put', 'patch']

    def dispatch(self, request, *args, **kwargs):
        self.payload = {
            'profile': {},
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
    

class UserHistoryViewSet(ModelViewSet):
    queryset = UserHistory.objects.all()
    serializer_class = UserHistorySerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        self.payload = {
            'history': [],
        }
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        self.payload['history'] = serializer.data
        # get solution and split into array
        for history in self.payload['history']:
            history['solution'] = history['solution'].split('.')
            history['solution'] = list(filter(lambda x: x != '', history['solution']))
        return Response(self.payload, status=status.HTTP_200_OK)
    

class ContactUsViewSet(ModelViewSet):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    http_method_names = ['post']
    authentication_classes = [] # Allow unauthenticated users
    permission_classes = [AllowAny] # Allow unauthenticated users

    def dispatch(self, request, *args, **kwargs):
        self.payload = {}
        return super().dispatch(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # send email to the admin
        send_mail(
            'Contact Us',
            f'Name: {serializer.validated_data["name"]}\nPhone: {serializer.validated_data["phone"]}\nEmail: {serializer.validated_data["email"]}\nMessage: {serializer.validated_data["message"]}',
            settings.EMAIL_HOST_USER,
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        self.payload['message'] = 'Message sent successfully!'
        return Response(self.payload, status=status.HTTP_200_OK)
