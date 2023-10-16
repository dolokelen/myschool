from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from . import models

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', "name"]

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolYear
        fields = ['id','year']