from django.contrib.auth.models import Group, Permission
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serializers

class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        permission_ids_to_remove = request.data.get('permissions_to_remove', [])
        permission_ids_to_add = request.data.get('permissions_to_add', [])

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

class SchoolYearViewSet(ModelViewSet):
    queryset = models.SchoolYear.objects.order_by('-year')
    serializer_class = serializers.SchoolYearSerializer



