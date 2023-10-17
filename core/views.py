from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet
from .models import User
from .serializers import GroupAddUserSerializer, GroupRemoveUserSerializer, UserCreateSerializer, UserUpdateSerializer


class UserModelViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserUpdateSerializer
        else:
            return UserCreateSerializer

    
class GroupAddUserView(CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupAddUserSerializer

    def perform_create(self, serializer):
        group = self.get_object()
        user_ids = self.request.data.get('user_ids', [])
        users = User.objects.filter(pk__in=user_ids)
        group.user_set.add(*users)

        return Response({'detail': 'Successfully added to group'}, status=status.HTTP_200_OK)

class GroupRemoveUserView(DestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupRemoveUserSerializer

    def perform_destroy(self, instance):
        group = self.get_object()
        user_ids = self.request.data.get('user_ids', [])
        users = User.objects.filter(pk__in=user_ids)
        group.user_set.remove(*users)

        return Response({'detail': 'Successfully removed'}, status=status.HTTP_200_OK)
    