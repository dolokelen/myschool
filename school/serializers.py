from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from . import models
from core.serializers import GroupAddUserSerializer, UserCreateSerializer

class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolYear
        fields = ['id','year']