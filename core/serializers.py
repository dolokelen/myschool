from django.contrib.auth.models import Group, Permission
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import User

class UserCreateSerializer(BaseUserCreateSerializer):
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'})
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        return super().create(validated_data)
    
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', "name"]

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

class SimpleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class GetUserAndGroupsSerializer(serializers.ModelSerializer):
    groups = SimpleGroupSerializer(many=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups']
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class AddGroupsToUserSerializer(serializers.ModelSerializer):
    group_ids = serializers.ListField(child=serializers.IntegerField())
    class Meta: 
        model = User
        fields = ['id', 'group_ids']
        
class GroupRemoveUserSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())
