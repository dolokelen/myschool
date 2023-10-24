from rest_framework import serializers
from . import models


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolYear
        fields = ['id', 'year']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = ['id', 'name', 'budget', 'duty']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'code', 'title', 'department', 'level', 'prerequisite',
                  'price_per_credit', 'credit', 'additional_fee']


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Semester
        fields = ['id', 'name', 'school_year', 'courses', 'enrollment_start_date',
                  'enrollment_end_date', 'start_date', 'end_date']
