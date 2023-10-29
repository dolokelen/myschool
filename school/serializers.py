from django.db import transaction
from rest_framework import serializers
from . import models


class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SchoolYear
        fields = ['id', 'year']


class DepartmentAddressSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()

    def create(self, validated_data):
        department_id = self.context['department_id']
        if department_id:
            instance = models.DepartmentAddress.objects.create(
                department_id=department_id, **validated_data)
            return instance

    class Meta:
        model = models.DepartmentAddress
        fields = ['country',
                  'county', 'city', 'district', 'community', 'department']


class DepartmentSerializer(serializers.ModelSerializer):
    number_of_courses = serializers.SerializerMethodField()
    departmentaddress = DepartmentAddressSerializer()

    def get_number_of_courses(self, department):
        return department.courses.count()

    def create(self, validated_data):
        department_address_data = validated_data.pop('departmentaddress')
        instance = models.Department.objects.create(**validated_data)
        models.DepartmentAddress.objects.create(
            department_id=instance.id, **department_address_data)

        return instance

    class Meta:
        model = models.Department
        fields = ['id', 'name', 'budget', 'duty',
                  'number_of_courses', 'created_at', 'departmentaddress']


class DepartmentContactSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()

    def create(self, validated_data):
        department_id = self.context['department_id']
        if department_id:
            instance = models.DepartmentContact.objects.create(
                department_id=department_id, **validated_data)
            return instance

    class Meta:
        model = models.DepartmentContact
        fields = ['id', 'phone', 'email', 'department']


class ReadCourseSerializer(serializers.ModelSerializer):#Review its impact and possibly delete it!!!
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


class ReadSemesterSerializer(serializers.ModelSerializer):
    school_year = serializers.StringRelatedField()
    courses = CourseSerializer(many=True)

    class Meta:
        model = models.Semester
        fields = ['id', 'name', 'school_year', 'enrollment_start_date',
                  'enrollment_end_date', 'start_date', 'end_date', 'is_current', 'courses']


class SemesterSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True, read_only=True)

    @transaction.atomic()
    def create(self, validated_data):
        semester = models.Semester.objects.create(**validated_data)
        courses = models.Course.objects \
            .select_related('prerequisite') \
            .select_related('department').all().distinct()
        semester.courses.set(courses)

        return semester

    class Meta:
        model = models.Semester
        fields = ['id', 'name', 'school_year', 'enrollment_start_date',
                  'enrollment_end_date', 'start_date', 'end_date', 'courses']
