from rest_framework import serializers
from . import models

class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolYear
        fields = ['year']