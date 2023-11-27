from django.db import transaction
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from core.serializers import UserCreateSerializer, SimpleUserSerializer
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


class SimpleCourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Course
        fields = ['id', 'code']


class DepartmentSerializer(serializers.ModelSerializer):
    departmentaddress = DepartmentAddressSerializer()
    departmentcontact = DepartmentContactSerializer(many=True)
    number_of_courses = serializers.SerializerMethodField()
    courses = SimpleCourseSerializer(many=True, read_only=True)

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
        fields = ['id', 'name', 'budget', 'duty', 'majors', 'courses',
                  'number_of_courses', 'created_at', 'departmentaddress', 'departmentcontact']


class SimpleDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = ['id', 'name']


class CoursePrerequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'code']


class SimpleSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = ['id', 'name']


class ReadCourseSerializer(serializers.ModelSerializer):
    departments = SimpleDepartmentSerializer(many=True)
    prerequisite = CoursePrerequisiteSerializer()
    total_price = serializers.SerializerMethodField()
    sections = SimpleSectionSerializer(many=True)

    def get_total_price(self, course):
        return (course.credit * course.price_per_credit) + course.additional_fee

    class Meta:
        model = models.Course
        fields = ['id', 'code', 'title', 'departments', 'level', 'prerequisite', 'sections',
                  'price_per_credit', 'credit', 'additional_fee', 'total_price']


class CourseSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, course):
        return (course.credit * course.price_per_credit) + course.additional_fee

    class Meta:
        model = models.Course
        fields = ['id', 'code', 'title', 'departments', 'level', 'prerequisite',
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
            .prefetch_related('departments').all().distinct()
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


class SimpleClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClassRoom
        fields = ['id', 'name', 'dimension']


class BuildingSerializer(serializers.ModelSerializer):
    buildingaddress = BuildingAddressSerializer()
    classrooms = SimpleClassRoomSerializer(many=True, read_only=True)

    @transaction.atomic()
    def create(self, validated_data):
        address_data = validated_data.pop('buildingaddress')
        instance = models.Building.objects.create(**validated_data)
        models.BuildingAddress.objects.create(
            building_id=instance.id, **address_data)

        return instance

    class Meta:
        model = models.Building
        fields = ['id', 'name', 'dimension', 'office_counts', 'classrooms',
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
    # The supervisor and office serializers are the promble for the ridiculous queries,
    # you could send an extra requests to their endpoints and then find the employee office and supervissor!!!
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


class SimpleStudentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = models.Student
        fields = ['user', 'level', 'phone']


class ReadTeacherSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    mentees = SimpleStudentSerializer(many=True)
    teacheraddress = TeacherAddressSerializer()
    office = ReadOfficeSerializer()
    supervisor = ReadTeacherSupervisorSerializer()
    department = SimpleDepartmentSerializer()
    joined_at = serializers.SerializerMethodField()

    def get_joined_at(self, employee):
        return employee.joined_at.strftime('%B %d, %Y')

    class Meta:
        model = models.Teacher
        fields = ['user', 'gender', 'marital_status', 'employment_status', 'birth_date', 'mentees',
                  'religion', 'level_of_education', 'salary', 'term_of_reference', 'image', 'department', 'phone',
                  'supervisor', 'office', 'joined_at', 'teacheraddress']


class SimpleTeacherSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.user.id

    def get_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'

    class Meta:
        model = models.Teacher
        fields = ['id', 'full_name']


class MajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Major
        fields = ['id', 'name', 'department']


class ReadMajorSerializer(serializers.ModelSerializer):
    department = SimpleDepartmentSerializer(read_only=True)

    class Meta:
        model = models.Major
        fields = ['id', 'name', 'department']


class SimpleMajorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Major
        fields = ['id', 'name']


class StudentAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAddress
        fields = ['country', 'county', 'city', 'district', 'community']


class ReadStudentSerializer(serializers.ModelSerializer):
    supervisor = SimpleTeacherSerializer()
    user = UserCreateSerializer()
    major = SimpleMajorSerializer()
    department = SimpleDepartmentSerializer()
    studentaddress = StudentAddressSerializer()

    class Meta:
        model = models.Student
        fields = ['user', 'birth_date', 'gender', 'religion', 'image', 'joined_at', 'student_number', 'is_transfer',
                  'level', 'department', 'supervisor', 'major', 'phone', 'registration_fee', 'studentaddress']


class StudentSerializer(serializers.ModelSerializer):
    user = UserCreateSerializer()
    studentaddress = StudentAddressSerializer()

    @transaction.atomic()
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        address_data = validated_data.pop('studentaddress')
        user_serializer = UserCreateSerializer(data=user_data)

        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.create(user_serializer.validated_data)
            instance = models.Student.objects.create(
                user_id=user.id, **validated_data)

            models.StudentAddress.objects.create(
                student_id=user.id, **address_data)

            return instance

    class Meta:
        model = models.Student
        fields = ['user', 'birth_date', 'gender', 'religion', 'image', 'joined_at', 'is_transfer',
                  'level', 'department', 'supervisor', 'major', 'phone', 'registration_fee', 'studentaddress']


class TeacherMenteeSerializer(serializers.ModelField):
    mentees = ReadStudentSerializer(many=True)

    class Meta:
        model = models.Teacher
        fields = ['mentees']


class ClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClassRoom
        fields = ['id', 'name', 'dimension', 'building']


class ReadClassRoomSerializer(serializers.ModelSerializer):
    building = SimpleBuildingSerializer()

    class Meta:
        model = models.ClassRoom
        fields = ['id', 'name', 'dimension', 'created_at', 'building']


class SimpleClassRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClassRoom
        fields = ['id', 'name']


class ClassTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ClassTime
        fields = ['id', 'start_time', 'end_time', 'week_days']


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = ['id', 'name', 'course', 'classroom', 'classtime']


class ReadSectionSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer()
    classroom = SimpleClassRoomSerializer()
    classtime = ClassTimeSerializer()

    class Meta:
        model = models.Section
        fields = ['id', 'name', 'course', 'classroom', 'classtime']


class SimpleSemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Semester
        fields = ['id', 'name']


class CurrentSemesterCourseSerializer(serializers.ModelSerializer):
    courses = SimpleCourseSerializer(many=True)

    class Meta:
        model = models.Semester
        fields = ['id', 'courses']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attendance
        fields = ['id', 'student', 'school_year', 'semester',
                  'course', 'section', 'mark', 'comment']


class ReadAttendanceSerializer(serializers.ModelSerializer):
    student = SimpleStudentSerializer()
    school_year = SchoolYearSerializer()
    semester = SimpleSemesterSerializer()
    course = SimpleCourseSerializer()
    section = SimpleSectionSerializer()

    class Meta:
        model = models.Attendance
        fields = ['id', 'student', 'school_year', 'semester',
                  'course', 'section', 'mark', 'comment', 'created_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Enrollment
        fields = ['id', 'student', 'course', 'section', 'semester',
                  'school_year', 'status', 'has_scholarship', 'date']


class ReadEnrollmentSerializer(serializers.ModelSerializer):
    student = SimpleStudentSerializer()
    course = SimpleCourseSerializer()
    section = SimpleSectionSerializer()
    semester = SimpleSemesterSerializer()
    school_year = SchoolYearSerializer()

    class Meta:
        model = models.Enrollment
        fields = ['id', 'student', 'course', 'section', 'course',
                  'semester', 'school_year', 'status', 'has_scholarship', 'date']


class CourseAndSectionsSerializer(serializers.ModelSerializer):
    sections = SimpleSectionSerializer(many=True)

    class Meta:
        model = models.Course
        fields = ['id', 'code', 'sections']


class TeachSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teach
        fields = ['id', 'teacher', 'course',
                  'section', 'semester', 'school_year']


class ReadTeachSerializer(serializers.ModelSerializer):
    teacher = SimpleTeacherSerializer()
    course = SimpleCourseSerializer()
    section = SimpleSectionSerializer()
    semester = SimpleSemesterSerializer()
    school_year = SchoolYearSerializer()

    class Meta:
        model = models.Teach
        fields = ['id', 'teacher', 'course', 'section',
                  'semester', 'school_year', 'date']


class SectionClassroomClasstimeSerializer(serializers.ModelSerializer):
    classtime = ClassTimeSerializer()
    classroom = SimpleClassRoomSerializer()

    class Meta:
        model = models.Section
        fields = ['id', 'name', 'classtime', 'classroom']


class UploadGradeSerializer(serializers.Serializer):
    excel_file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['xlsx'])])


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Grade
        fields = ['id', 'student', 'school_year', 'semester', 'course', 'section',
                  'attendance', 'quiz', 'assignment', 'midterm', 'project', 'final']


class ReadGradeSerializer(serializers.ModelSerializer):
    POINT_FOR_LETTER_A_GRADE = 4
    POINT_FOR_LETTER_B_GRADE = 3
    POINT_FOR_LETTER_C_GRADE = 2
    POINT_FOR_LETTER_D_GRADE = 1

    student = SimpleStudentSerializer()
    school_year = SchoolYearSerializer()
    course = SimpleCourseSerializer()
    section = SimpleSectionSerializer()
    letter = serializers.SerializerMethodField()
    grade_point = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()

    def get_letter(self, obj):
        avg = avg = self.get_average(obj)
        if avg >= 90:
            return 'A'
        if avg >= 80:
            return 'B'
        if avg >= 70:
            return 'C'
        if avg >= 60:
            return 'D'
        return 'F'
    
    def get_total_score(self, obj):
        return self.get_average(obj)
    
    def get_average(self, obj):
        return int(obj.attendance) + int(obj.assignment) + int(obj.quiz) + int(obj.midterm) + int(obj.project) + int(obj.final)

    def get_grade_point(self, obj):
        avg = self.get_average(obj)
        credit = models.Course.objects.get(code=obj.course.code).credit
        return self.calc_grade_point(credit, avg)
            
    def calc_grade_point(self, credit, avg):
        if avg >= 90:
            return credit * self.POINT_FOR_LETTER_A_GRADE
        if avg >= 80:
            return credit * self.POINT_FOR_LETTER_B_GRADE
        if avg >= 70:
            return credit * self.POINT_FOR_LETTER_C_GRADE
        if avg >= 60:
            return credit * self.POINT_FOR_LETTER_D_GRADE
        return 0

    class Meta:
        model = models.Grade
        fields = ['id', 'student', 'school_year', 'semester', 'course', 'section', 'attendance', 
                  'quiz', 'assignment', 'midterm', 'project', 'final', 'letter', 'grade_point', 'total_score']


