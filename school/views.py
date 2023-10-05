from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from . import models
from . import serializers

class SchoolYearViewSet(ModelViewSet):
    queryset = models.SchoolYear.objects.all()
    serializer_class = serializers.SchoolYearSerializer
