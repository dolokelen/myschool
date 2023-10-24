from django_filters.rest_framework import FilterSet
from . import models

class CourseFilter(FilterSet):
    class Meta:
        model = models.Course
        fields = {
            'department_id': ['exact'],
            'prerequisite': ['exact']
        }