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


class SimpleDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = ['id', 'name']


class CoursePrerequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'code']


class ReadCourseSerializer(serializers.ModelSerializer):
    department = SimpleDepartmentSerializer()
    prerequisite = CoursePrerequisiteSerializer()
    total_price = serializers.SerializerMethodField()

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


class EmployeeAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeeAddress
        fields = ['country', 'county', 'city', 'district', 'community']


class EmployeeSerializer(serializers.ModelSerializer):
    employeeaddress = EmployeeAddressSerializer()
    user = UserCreateSerializer()

    @transaction.atomic()
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        address_data = validated_data.pop('employeeaddress')
        user_serializer = UserCreateSerializer(data=user_data)

        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.create(user_serializer.validated_data)
            instance = models.Employee.objects.create(
                user_id=user.id, **validated_data)
            models.EmployeeAddress.objects.create(
                employee_id=user.id, **address_data)

            return instance

    class Meta:
        model = models.Employee
        fields = ['user', 'gender', 'marital_status', 'employment_status', 'birth_date',
                  'religion', 'salary', 'term_of_reference', 'image', 'department',
                  'supervisor', 'office', 'phone', 'level_of_education', 'employeeaddress']


class ReadableSupervisorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_full_name(self, employee):
        return f'{employee.user.first_name} {employee.user.last_name}'

    def get_id(self, employee):
        return employee.user.id

    class Meta:
        model = models.Employee
        fields = ['id', 'full_name']


class ReadEmployeeSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    employeeaddress = EmployeeAddressSerializer()
    office = ReadOfficeSerializer()
    supervisor = ReadableSupervisorSerializer()
    department = SimpleDepartmentSerializer()
    joined_at = serializers.SerializerMethodField()

    def get_joined_at(self, employee):
        return employee.joined_at.strftime('%B %d, %Y')

    class Meta:
        model = models.Employee
        fields = ['user', 'gender', 'marital_status', 'employment_status', 'birth_date',
                  'religion', 'level_of_education', 'salary', 'term_of_reference', 'image', 'department', 'phone',
                  'supervisor', 'office', 'joined_at', 'employeeaddress']


class TeacherAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TeacherAddress
        fields = ['country', 'county', 'city', 'district', 'community']



class TeacherSerializer(serializers.ModelSerializer):
    teacheraddress = TeacherAddressSerializer()
    user = UserCreateSerializer()

    @transaction.atomic()
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        address_data = validated_data.pop('teacheraddress')
        user_serializer = UserCreateSerializer(data=user_data)

        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.create(user_serializer.validated_data)
            instance = models.Teacher.objects.create(
                user_id=user.id, **validated_data)

            models.TeacherAddress.objects.create(
                teacher_id=user.id, **address_data)

            return instance

    class Meta:
        model = models.Teacher
        fields = ['user', 'gender', 'marital_status', 'employment_status', 'birth_date',
                  'religion', 'salary', 'term_of_reference', 'image', 'department',
                  'supervisor', 'office', 'phone', 'level_of_education', 'teacheraddress']


class ReadTeacherSupervisorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def get_full_name(self, teacher):
        return f'{teacher.user.first_name} {teacher.user.last_name}'

    def get_id(self, teacher):
        return teacher.user.id

    class Meta:
        model = models.Teacher
        fields = ['id', 'full_name']


class ReadTeacherSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    teacheraddress = TeacherAddressSerializer()
    office = ReadOfficeSerializer()
    supervisor = ReadTeacherSupervisorSerializer()
    department = SimpleDepartmentSerializer()
    joined_at = serializers.SerializerMethodField()

    def get_joined_at(self, employee):
        return employee.joined_at.strftime('%B %d, %Y')

    class Meta:
        model = models.Teacher
        fields = ['user', 'gender', 'marital_status', 'employment_status', 'birth_date',
                  'religion', 'level_of_education', 'salary', 'term_of_reference', 'image', 'department', 'phone',
                  'supervisor', 'office', 'joined_at', 'teacheraddress']
