from accounts.models import User, UserHistory
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from api.serializers.accounts import (
    UserSerializer, UserHistorySerializer
)


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
        return Response(self.payload, status=status.HTTP_200_OK)
