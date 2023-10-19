from django.contrib.auth.models import Group, Permission
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import User
from . import serializers

class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        permission_ids_to_remove = request.data.get('permission_ids_to_remove', [])
        permission_ids_to_add = request.data.get('permission_ids_to_add', [])

        if permission_ids_to_remove:
            permissions_to_remove = instance.permissions.filter(id__in=permission_ids_to_remove)
            instance.permissions.remove(*permissions_to_remove)
            return Response({'detail': 'Permissions removed successfully'}, status=status.HTTP_200_OK)
        elif permission_ids_to_add:
            query_set = instance.permissions.all()
            existing_permission_ids = query_set.values_list('id', flat=True)
            combine_permissions = list(existing_permission_ids) + permission_ids_to_add
            instance.permissions.set(combine_permissions)
            return Response({'detail': 'Permissions added successfully'})
        else:
            serializer = serializers.GroupSerializer(instance, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'detail': 'Group name updated successfully'}, status=status.HTTP_200_OK)

class PermissionViewSet(ModelViewSet):
    http_method_names = ['get', 'post']
    excluded_ids = [1, 2, 3, 4, 13, 14, 15, 16, 17, 18, 19, 20]
    queryset = Permission.objects.exclude(id__in=excluded_ids)
    serializer_class = serializers.PermissionSerializer

class UserViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.GetUserAndGroupsSerializer
        if self.request.method == 'PATCH':
            if 'group_ids' in self.request.data:
                return serializers.AddGroupsToUserSerializer
            return serializers.UserUpdateSerializer
        else:
            return serializers.UserCreateSerializer
    
    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        group_to_add_ids = request.data.get('group_to_add_ids', [])
        group_to_remove_ids = request.data.get('group_to_remove_ids', [])

        if group_to_add_ids:
            groups = Group.objects.filter(pk__in=group_to_add_ids)
            user.groups.add(*groups)
            return Response({'detail': 'Groups successfully added'})
        if group_to_remove_ids:
            groups = Group.objects.filter(pk__in=group_to_remove_ids)
            user.groups.remove(*groups)
            return Response({'detail': 'Groups successfully removed'})
        else:
            serializer = serializers.UserUpdateSerializer(user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response({'detail': 'Record updated successfully'})


def index(request):
    return render(request, 'index.html')


