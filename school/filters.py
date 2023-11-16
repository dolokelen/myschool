from django_filters.rest_framework import FilterSet
from . import models

class CourseFilter(FilterSet):
    class Meta:
        model = models.Course
        fields = {
            'prerequisite': ['exact']
        }


class EmployeeFilter(FilterSet):
    class Meta:
        model = models.Employee
        fields = {
            'department_id': ['exact'],
        }


class MajorFilter(FilterSet):
    class Meta:
        model = models.Major
        fields = {
            'department_id': ['exact'],
        }


class TeacherFilter(FilterSet):
    class Meta:
        model = models.Teacher
        fields = {
            'department_id': ['exact'],
        }

class StudentFilter(FilterSet):
    class Meta:
        model = models.Student
        fields = {
            'department_id': ['exact'],
            'major_id': ['exact'],
        }