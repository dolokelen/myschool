from django.contrib.auth.models import Group, Permission
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serializers

class SchoolYearViewSet(ModelViewSet):
    queryset = models.SchoolYear.objects.order_by('-year')
    serializer_class = serializers.SchoolYearSerializer



