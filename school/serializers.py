from rest_framework import serializers
from . import models


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolYear
        fields = ['id', 'year']

class DepartmentSerializer(serializers.ModelSerializer):
    number_of_courses = serializers.SerializerMethodField()

    def get_number_of_courses(self, department):
        return department.courses.count()
    class Meta:
        model = models.Department
        fields = ['id', 'name', 'budget', 'duty', 'number_of_courses', 'created_at']

class ReadCourseSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()
    prerequisite = serializers.StringRelatedField()
    level = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    def get_level(self, course):
        return course.get_level_display()
    
    def get_total_price(self, course):
        return (course.credit * course.price_per_credit) + course.additional_fee

    class Meta:
        model = models.Course
        fields = ['id', 'code', 'title', 'department', 'level', 'prerequisite',
                  'price_per_credit', 'credit', 'additional_fee', 'total_price']

class CourseSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self, course):
        return (course.credit * course.price_per_credit) + course.additional_fee

    class Meta:
        model = models.Course
        fields = ['id', 'code', 'title', 'department', 'level', 'prerequisite',
                  'price_per_credit', 'credit', 'additional_fee', 'total_price']

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Semester
        fields = ['id', 'name', 'school_year', 'courses', 'enrollment_start_date',
                  'enrollment_end_date', 'start_date', 'end_date']
