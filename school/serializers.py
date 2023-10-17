from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from . import models
from core.serializers import GroupAddUserSerializer, UserCreateSerializer
#Everythin concerning profile, group and permission should go in the core app!!!!

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', "name"]

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    users = UserCreateSerializer(many=True, read_only=True, source='user_set')
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'users']

class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolYear
        fields = ['id','year']