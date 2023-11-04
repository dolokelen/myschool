from django.db import transaction
from rest_framework import serializers
from core.serializers import UserCreateSerializer
from core.models import User
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


class DepartmentSerializer(serializers.ModelSerializer):
    departmentaddress = DepartmentAddressSerializer()
    departmentcontact = DepartmentContactSerializer(many=True)
    number_of_courses = serializers.SerializerMethodField()

    def get_number_of_courses(self, department):
        return department.courses.count()

    @transaction.atomic()
    def create(self, validated_data):
        department_address_data = validated_data.pop('departmentaddress')
        department_contact_data = validated_data.pop('departmentcontact')

        instance = models.Department.objects.create(**validated_data)
        models.DepartmentAddress.objects.create(
            department_id=instance.id, **department_address_data)

        for contact_data in department_contact_data:
            models.DepartmentContact.objects.create(
                department_id=instance.id, **contact_data)

        return instance

    class Meta:
        model = models.Department
        fields = ['id', 'name', 'budget', 'duty',
                  'number_of_courses', 'created_at', 'departmentaddress', 'departmentcontact']


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


class ReadSemesterSerializer(serializers.ModelSerializer):
    school_year = SchoolYearSerializer(read_only=True)
    courses = CourseSerializer(many=True, read_only=True)

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


class BuildingAddressSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        building_id = self.context['building_id']
        instance = models.BuildingAddress.objects.create(
            building_id=building_id, **validated_data)

        return instance

    class Meta:
        model = models.BuildingAddress
        fields = ['country', 'county', 'city', 'district', 'community']


class BuildingSerializer(serializers.ModelSerializer):
    buildingaddress = BuildingAddressSerializer()

    @transaction.atomic()
    def create(self, validated_data):
        address_data = validated_data.pop('buildingaddress')
        instance = models.Building.objects.create(**validated_data)
        models.BuildingAddress.objects.create(
            building_id=instance.id, **address_data)

        return instance

    class Meta:
        model = models.Building
        fields = ['id', 'name', 'dimension', 'office_counts',
                  'classroom_counts', 'toilet_counts', 'date_constructed', 'buildingaddress']


class SimpleBuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Building
        fields = ['id', 'name']


class ReadOfficeSerializer(serializers.ModelSerializer):
    building = SimpleBuildingSerializer(read_only=True)

    class Meta:
        model = models.Office
        fields = ['id', 'dimension', 'building']


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Office
        fields = ['id', 'dimension', 'building']


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()

    @transaction.atomic()
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data.pop('confirm_password')
        user = User.objects.create(**user_data)
        instance = models.Employee.objects.create(
            user_id=user.id, **validated_data)

        return instance

    class Meta:
        model = models.Employee
        fields = ['user', 'gender', 'marital_status', 'employment_status', 'birth_date',
                  'religion', 'salary', 'term_of_reference', 'image', 'department', 'supervisor', 'office']


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()

    class Meta:
        model = models.Employee
        fields = ['user', 'gender', 'marital_status', 'employment_status', 'birth_date',
                  'religion', 'salary', 'department', 'supervisor', 'office']
