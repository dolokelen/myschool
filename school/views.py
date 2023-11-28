import pandas as pd
from django.db import transaction
from django.db.models import Prefetch, Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from core.models import User
from core import serializers as core_serializers
from . import models, serializers, permissions, filters


class Permission(ModelViewSet):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.ReadModelPermission()]
        if self.request.method == 'POST':
            return [permissions.CreateModelPermission()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.UpdateModelPermission()]
        if self.request.method == 'DELETE':
            return [permissions.DeleteModelPermission()]


class SchoolYearViewSet(Permission):
    queryset = models.SchoolYear.objects.all()
    serializer_class = serializers.SchoolYearSerializer


class DepartmentViewSet(Permission):
    queryset = models.Department.objects.prefetch_related('courses')\
        .select_related('departmentaddress').\
        prefetch_related('departmentcontact').prefetch_related('majors').all()
    serializer_class = serializers.DepartmentSerializer


class DepartmentAddressViewSet(ModelViewSet):
    serializer_class = serializers.DepartmentAddressSerializer

    def get_queryset(self):
        department_address = models.DepartmentAddress.objects.filter(
            department=self.kwargs['departments_pk'])
        return department_address

    def get_serializer_context(self):
        return {'department_id': self.kwargs['departments_pk']}


class DepartmentContactViewSet(ModelViewSet):
    serializer_class = serializers.DepartmentContactSerializer

    def get_queryset(self):
        department_contact = models.DepartmentContact.objects.filter(
            department=self.kwargs['departments_pk'])
        return department_contact

    def get_serializer_context(self):
        return {'department_id': self.kwargs['departments_pk']}


class CourseViewSet(Permission):
    queryset = models.Course.objects.select_related(
        'prerequisite').prefetch_related('departments').prefetch_related('sections').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = filters.CourseFilter
    search_fields = ['code', 'title']
    ordering_fields = ['price_per_credit', 'credit', 'additional_fee']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadCourseSerializer
        return serializers.CourseSerializer


class SemesterViewSet(Permission):
    queryset = models.Semester.objects.select_related('school_year').\
        prefetch_related('courses').all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['name', 'is_current']

    def partial_update(self, request, *args, **kwargs):
        semester = self.get_object()
        courses_to_add_ids = request.data.get('courses_to_add_ids', [])
        courses_to_remove_ids = request.data.get('courses_to_remove_ids', [])
        if courses_to_add_ids:
            existing_courses = semester.courses.all()
            existing_courses_ids = existing_courses.values_list(
                'id', flat=True)
            combined_courses = list(existing_courses_ids) + courses_to_add_ids
            semester.courses.set(combined_courses)
        elif courses_to_remove_ids:
            semester.courses.remove(*courses_to_remove_ids)

        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadSemesterSerializer
        return serializers.SemesterSerializer


class BuildingViewSet(Permission):
    queryset = models.Building.objects.select_related(
        'buildingaddress').prefetch_related('classrooms').all()
    serializer_class = serializers.BuildingSerializer


class BuildingAddressViewSet(ModelViewSet):
    serializer_class = serializers.BuildingAddressSerializer

    def get_queryset(self):
        building_address = models.BuildingAddress.objects.filter(
            building_id=self.kwargs['buildings_pk'])

        return building_address

    def get_serializer_context(self):
        return {'building_id': self.kwargs['buildings_pk']}


class OfficeViewSet(Permission):
    queryset = models.Office.objects.select_related('building').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadOfficeSerializer
        return serializers.OfficeSerializer


class EmployeeViewSet(Permission):
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.EmployeeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = models.Employee.objects.select_related('user').select_related(
        'office').select_related('department').select_related('supervisor')\
        .select_related('employeeaddress').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadEmployeeSerializer
        return serializers.EmployeeSerializer

    @transaction.atomic()
    def partial_update(self, request, *args, **kwargs):
        mutable_data = self.request.data.copy()
        user_id = self.kwargs['pk']

        user_data = {
            'username': mutable_data.pop('user.username')[0],
            'email': mutable_data.pop('user.email')[0],
            'first_name': mutable_data.pop('user.first_name')[0],
            'last_name': mutable_data.pop('user.last_name')[0],
            'is_active': mutable_data.pop('user.is_active')[0],
        }
        address_data = {
            'country': mutable_data.pop('employeeaddress.country')[0],
            'county': mutable_data.pop('employeeaddress.county')[0],
            'city': mutable_data.pop('employeeaddress.city')[0],
            'district': mutable_data.pop('employeeaddress.district')[0],
            'community': mutable_data.pop('employeeaddress.community')[0],
        }

        user_instance = self.update_user(user_data, user_id)
        self.update_address(address_data, user_id)

        if user_instance is None:
            return Response({'user': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

        employee_instance = self.get_object()
        if mutable_data['supervisor'][0] == '0':
            mutable_data['supervisor'] = None

        serializer = self.get_serializer(
            employee_instance, data=mutable_data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def update_user(self, user_data, user_id):
        try:
            user_instance = User.objects.get(id=user_id)
            serializer = core_serializers.UserUpdateSerializer(
                user_instance, data=user_data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return user_instance
        except User.DoesNotExist:
            return None

    def update_address(self, address_data, user_id):
        address_instance = models.EmployeeAddress.objects.get(
            employee_id=user_id)
        serializer = serializers.EmployeeAddressSerializer(
            address_instance, data=address_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return address_instance

    def create(self, request, *args, **kwargs):
        supervisor = self.request.data.get('supervisor', None)

        if supervisor == '0':
            self.request.data['supervisor'] = None

        return super().create(request, *args, **kwargs)


class EmployeeProfileViewSet(ModelViewSet):
    http_method_names = ['get']
    serializer_class = serializers.ReadEmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.Employee.objects.filter(user_id=self.kwargs['pk'])
        return queryset


class TeacherViewSet(Permission):
    # Only return current semester teacher just how you did course.
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.TeacherFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = models.Teacher.objects.select_related('user').select_related(
        'office').select_related('department').select_related('supervisor')\
        .select_related('teacheraddress').prefetch_related('mentees').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadTeacherSerializer
        return serializers.TeacherSerializer

    @transaction.atomic()
    def partial_update(self, request, *args, **kwargs):
        mutable_data = self.request.data.copy()
        user_id = self.kwargs['pk']

        user_data = {
            'username': mutable_data.pop('user.username')[0],
            'email': mutable_data.pop('user.email')[0],
            'first_name': mutable_data.pop('user.first_name')[0],
            'last_name': mutable_data.pop('user.last_name')[0],
            'is_active': mutable_data.pop('user.is_active')[0],
        }
        address_data = {
            'country': mutable_data.pop('teacheraddress.country')[0],
            'county': mutable_data.pop('teacheraddress.county')[0],
            'city': mutable_data.pop('teacheraddress.city')[0],
            'district': mutable_data.pop('teacheraddress.district')[0],
            'community': mutable_data.pop('teacheraddress.community')[0],
        }
        user_instance = self.update_user(user_data, user_id)
        self.update_address(address_data, user_id)

        if user_instance is None:
            return Response({'user': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

        teacher_instance = self.get_object()
        if mutable_data['supervisor'][0] == '0':
            mutable_data['supervisor'] = None

        serializer = self.get_serializer(
            teacher_instance, data=mutable_data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def update_user(self, user_data, user_id):
        try:
            user_instance = User.objects.get(id=user_id)
            serializer = core_serializers.UserUpdateSerializer(
                user_instance, data=user_data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return user_instance
        except User.DoesNotExist:
            return None

    def update_address(self, address_data, user_id):
        address_instance = models.TeacherAddress.objects.get(
            teacher_id=user_id)
        serializer = serializers.TeacherAddressSerializer(
            address_instance, data=address_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return address_instance

    def create(self, request, *args, **kwargs):
        supervisor = self.request.data.get('supervisor', None)

        if supervisor == '0':
            self.request.data['supervisor'] = None

        return super().create(request, *args, **kwargs)


class TeacherProfileViewSet(ModelViewSet):
    http_method_names = ['get']
    serializer_class = serializers.ReadTeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.Teacher.objects.filter(user_id=self.kwargs['pk'])
        return queryset


class MajorViewSet(Permission):
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.MajorFilter
    queryset = models.Major.objects.select_related('department').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadMajorSerializer
        return serializers.MajorSerializer


class StudentViewSet(Permission):
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = filters.StudentFilter
    search_fields = ['phone', 'level', 'religion', 'gender', 'student_number']

    queryset = models.Student.objects.select_related('user').select_related(
        'supervisor').select_related('major').select_related('department').\
        select_related('studentaddress').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadStudentSerializer
        return serializers.StudentSerializer

    @transaction.atomic()
    def partial_update(self, request, *args, **kwargs):
        mutable_data = self.request.data.copy()
        user_id = self.kwargs['pk']

        user_data = {
            'username': mutable_data.pop('user.username')[0],
            'email': mutable_data.pop('user.email')[0],
            'first_name': mutable_data.pop('user.first_name')[0],
            'last_name': mutable_data.pop('user.last_name')[0],
            'is_active': mutable_data.pop('user.is_active')[0],
        }
        address_data = {
            'country': mutable_data.pop('studentaddress.country')[0],
            'county': mutable_data.pop('studentaddress.county')[0],
            'city': mutable_data.pop('studentaddress.city')[0],
            'district': mutable_data.pop('studentaddress.district')[0],
            'community': mutable_data.pop('studentaddress.community')[0],
        }
        user_instance = self.update_user(user_data, user_id)
        self.update_address(address_data, user_id)

        if user_instance is None:
            return Response({'user': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

        student_instance = self.get_object()
        serializer = self.get_serializer(
            student_instance, data=mutable_data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def update_user(self, user_data, user_id):
        try:
            user_instance = User.objects.get(id=user_id)
            serializer = core_serializers.UserUpdateSerializer(
                user_instance, data=user_data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return user_instance
        except User.DoesNotExist:
            return None

    def update_address(self, address_data, user_id):
        address_instance = models.StudentAddress.objects.get(
            student_id=user_id)
        serializer = serializers.StudentAddressSerializer(
            address_instance, data=address_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return address_instance


class StudentProfileViewSet(ModelViewSet):
    http_method_names = ['get']
    serializer_class = serializers.ReadStudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.Student.objects.filter(user_id=self.kwargs['pk'])
        return queryset
    

class ClassRoomViewSet(Permission):
    queryset = models.ClassRoom.objects.select_related('building').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadClassRoomSerializer
        return serializers.ClassRoomSerializer


class ClassTimeViewSet(Permission):
    queryset = models.ClassTime.objects.all()
    serializer_class = serializers.ClassTimeSerializer


class SectionViewSet(Permission):
    queryset = models.Section.objects.select_related('course').select_related('classtime')\
        .select_related('classroom').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadSectionSerializer
        return serializers.SectionSerializer


class CurrentSemesterCourseViewSet(Permission):
    http_method_names = ['get']
    serializer_class = serializers.CurrentSemesterCourseSerializer

    def get_queryset(self):
        current_semester = models.Semester.objects.filter(is_current=True)
        return current_semester


class AttendanceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = models.Attendance.objects.filter(section_id=self.kwargs['sections_pk'])\
            .select_related('student').select_related('course')\
            .select_related('school_year').select_related('semester').select_related('section')
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadAttendanceSerializer
        return serializers.AttendanceSerializer

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        for attendance in request.data:
            serializer = self.get_serializer(data=attendance)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnrollmentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadEnrollmentSerializer
        return serializers.EnrollmentSerializer

    def get_queryset(self):
        student_id = self.kwargs['students_pk']
        try:
            student_obj = models.Student.objects.get(user_id=student_id)
        except models.Student.DoesNotExist:
            return Response({'error': 'student does not exist'}, status=status.HTTP_404_NOT_FOUND)

        student_enrollments = student_obj.enrollments.select_related('course',
                                                                     'section',
                                                                     'semester',
                                                                     'school_year',).all()

        return student_enrollments


class StudentEligibleCourseViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    serializer_class = serializers.CourseAndSectionsSerializer

    def get_queryset(self):
        student_id = self.kwargs['students_pk']
        # You also have to ensure that the student has a passing mark for the prerequisite for that course.

        try:
            student_obj = models.Student.objects.get(user_id=student_id)
        except models.Student.DoesNotExist:
            return Response({'error': 'student does not exist'}, status=status.HTTP_404_NOT_FOUND)

        student_enrollments = student_obj.enrollments.select_related('course',
                                                                     'section',
                                                                     'semester',
                                                                     'school_year',).all()
        completed_courses = [cos.course.code for cos in student_enrollments]

        student_department = student_obj.department
        department_courses = student_department.courses.select_related(
            'prerequisite').prefetch_related('departments').all()
        current_courses = department_courses.filter(semesters__is_current=True)

        eligible_courses = []

        for course in current_courses:
            prerequisite = course.prerequisite

            if (not prerequisite and course.code not in completed_courses) or \
                    (prerequisite and prerequisite.code in completed_courses and course.code not in completed_courses):

                eligible_courses.append(course)

        return eligible_courses


class CurrentSemesterSectionEnrollmentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    serializer_class = serializers.ReadEnrollmentSerializer

    def get_queryset(self):
        section_id = self.kwargs['sections_pk']

        try:
            section_obj = models.Section.objects.get(id=section_id)
        except models.Section.DoesNotExist:
            return Response({'error': "Section does not exist"}, status=status.HTTP_404_NOT_FOUND)

        course_id = section_obj.course.id
        curr_enrollments = models.Enrollment.objects.filter(course_id=course_id, section_id=section_obj.id, semester__is_current=True).\
            select_related('school_year', 'semester',
                           'course', 'student', 'section')

        return curr_enrollments


def prefetch_enrollments():
    prefetch_query = Prefetch(
        'section__enrollments',
        queryset=models.Enrollment.objects.filter(
            Q(status='Approved') & Q(semester__is_current=True)
        ).select_related('student', 'course', 'semester', 'school_year', 'section'),
        to_attr='approved_enrollments'
    )
    return prefetch_query

# def prefetch_enrollments():
#     prefetch_query = Prefetch(
#         'section__enrollments',
#         queryset=models.Enrollment.objects.filter(
#             Q(status='Approved') & Q(semester__is_current=True)
#         ).select_related('student', 'course', 'semester', 'school_year', 'section'),
#         to_attr='approved_enrollments'
#     )
#     return prefetch_query


class TeachAndSectionEnrollmentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        try:
            teacher = models.Teacher.objects.get(
                user_id=self.kwargs['teachers_pk'])
        except models.Teacher.DoesNotExist:
            return Response({'error': 'Teacher does not exist'})

        teaches = teacher.teaches.select_related(
            'course', 'section', 'school_year', 'semester', 'teacher',
        ).prefetch_related(prefetch_enrollments()).all()

        assigned_courses = set(
            enrollment for teach in teaches for enrollment in teach.section.approved_enrollments)
        return assigned_courses

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadEnrollmentSerializer
        return serializers.TeachSerializer


class SectionClasstimeViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    serializer_class = serializers.ClassTimeSerializer

    def get_queryset(self):
        section_id = self.kwargs['sections_pk']

        queryset = models.ClassTime.objects.filter(sections=section_id)
        return queryset


class SectionClassroomViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    serializer_class = serializers.ReadClassRoomSerializer

    def get_queryset(self):
        section_id = self.kwargs['sections_pk']

        queryset = models.ClassRoom.objects.filter(
            sections=section_id).select_related('building')
        return queryset


class OnlyCourseWithSectionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    serializer_class = serializers.CourseAndSectionsSerializer

    # def get_queryset(self):
    # teaches = models.Teach.objects.filter(semester__is_current=True).select_related('course', 'section', 'semester', 'school_year', 'teacher')
    # assigned_course_section = [{teach.course.id: teach.section.id} for teach in teaches]
    # queryset = models.Course.objects.filter(semesters__is_current=True).prefetch_related('sections')
    # all_courses_sections = [course for course in queryset if course.sections.all()]
    # both_assigned_unassigned = [{course.id: [section.id for section in course.sections.all()]} for course in all_courses_sections]

    # print('********BOTH: ', both_assigned_unassigned)
    # print('********ASSIGNED: ', assigned_course_section)

    # available_sections = []

    # for assigned_dict in assigned_course_section:
    #     for course_id, sec_id in assigned_dict.items():
    #         for unassigned_dict in both_assigned_unassigned:
    #             if course_id in unassigned_dict and sec_id in unassigned_dict[course_id]:
    #                 unassigned_dict[course_id].remove(sec_id)
    #                 if unassigned_dict[course_id]:
    #                     print('******REMAING SECTIONS', unassigned_dict[course_id])
    #                     course = models.Course.objects.get(id=course_id)
    #                     for section in course.sections.all():
    #                         if section.id not in unassigned_dict[course_id]:
    #                             course.sections.remove(section)
    #                     print('Retrieved COURSE SECTIONS', [s.name for s in course.sections.all()])
    #                     course.sections.set(models.Section.objects.filter(id__in=unassigned_dict[course_id]))
    #                     print('*****SET SECTIONS', [s.name for s in course.sections.all()])
    #                     available_sections.append(course)
    #                     # available_sections.append({course_id: unassigned_dict[course_id]})
    #                     # available_sections.append(models.Course(id=course_id, sections=models.Section.objects.filter(id__in=unassigned_dict[course_id])))
    # print('********AVAILABLE SECTIONS: ', available_sections)
    # return available_sections

    def get_queryset(self):
        queryset = models.Course.objects.filter(
            semesters__is_current=True).prefetch_related('sections')
        return [course for course in queryset if course.sections.all()]


class TeacherAssignSectionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    serializer_class = serializers.ReadTeachSerializer

    def get_queryset(self):
        teacher_id = self.kwargs['teachers_pk']

        try:
            _ = models.Teacher.objects.get(user_id=teacher_id)
        except models.Teacher.DoesNotExist:
            return Response({'error': 'Teacher does not exist'})

        return models.Teach.objects.filter(teacher_id=teacher_id, semester__is_current=True).\
            select_related('course', 'section', 'school_year',
                           'semester', 'teacher')


class TeachUpdateViewSet(Permission):
    queryset = models.Teach.objects.select_related(
        'course', 'teacher', 'semester', 'school_year', 'section').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadTeachSerializer
        return serializers.TeachSerializer


class GradeViewSet(ModelViewSet):
    # permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'put', 'patch']
    queryset = models.Grade.objects.select_related('student', 'school_year', 'semester', 'course', 'section').all()
    serializer_class = serializers.ReadGradeSerializer
    
    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        teacher_obj = self.get_teacher(self.kwargs['teachers_pk'])
        teach_id = self.get_teach_id(self.kwargs['teaches_pk'])

        serializer = serializers.UploadGradeSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            teach = teacher_obj.teaches.filter(
                id=teach_id, semester__is_current=True).first()

            if not teach:
                return Response({'error': 'Teacher record does not exist'}, status=status.HTTP_404_NOT_FOUND)

            grades_file = serializer.validated_data['excel_file']
            try:
                grades_file_rows = pd.read_excel(grades_file, header=None)
                excluded_indexes = self.get_excluded_indexes()
                students = self.get_grades_file_students_list(grades_file_rows, excluded_indexes)

            except pd.errors.ParserError as e:
                return Response({'error': f'Error reading the file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            enrollments_list = self.get_enrollments_list(teach)

            if len(students) != len(enrollments_list):
                return Response({'error': 'Incomplete students listing'}, status=status.HTTP_401_UNAUTHORIZED)

            for student in students:
                if student not in enrollments_list:
                    return Response({'error': 'Unknown student found in spreadsheet'}, 
                                    status=status.HTTP_403_FORBIDDEN)
            self.create_grades(grades_file_rows, teach, excluded_indexes)
            
        return Response({'success': True}, status=status.HTTP_201_CREATED)
    
    def get_teacher(self, teacher_id):
        try:
            teacher_obj = models.Teacher.objects.get(user_id=teacher_id)
        except models.Teacher.DoesNotExist:
            return Response({'error': 'Teacher does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return teacher_obj
    
    def get_teach_id(self, teach_id):
        try:
            id = models.Teach.objects.get(id=teach_id).id
        except models.Teach.DoesNotExist:
            return Response({'error': 'This section does not exist for the teacher'}, status=status.HTTP_404_NOT_FOUND)
        return id

    def get_excluded_indexes(self):
        semester_row = 0
        school_year_row = 1
        course_row = 2
        section_row = 3
        student_record_header = 4
        excluded_indexes = [semester_row, school_year_row,
                                    course_row, section_row, student_record_header]
        return excluded_indexes
            
    @transaction.atomic()
    def create_grades(self, grades_file_rows, teach, excluded_indexes):
        for index, row in grades_file_rows.iterrows():
            if index not in excluded_indexes:
                models.Grade.objects.create(
                school_year_id=teach.school_year.id, semester_id=teach.semester.id, course_id=teach.course.id, 
                section_id=teach.section.id, student_id=row.loc[0], attendance=row.loc[1], assignment=row.loc[2], 
                quiz=row.loc[3], midterm=row.loc[4], project=row.loc[5], final=row.loc[6])
                
    def get_enrollments_list(self, teach):
        enrollments = models.Enrollment.objects.filter(
                course=teach.course, section=teach.section, semester__is_current=True).values_list('student', flat=True)
        return list(enrollments)
    
    def get_grades_file_students_list(self, grades_file_rows, excluded_indexes):
        students = []
        for index, row in grades_file_rows.iterrows():
            if index not in excluded_indexes:
                try:
                    students.append(row.loc[0])
                except KeyError:
                    pass
        return students
    

class StudentGradeAccessViewSet(ModelViewSet):
    """
    Returns all grades for a student more like a transcript
    """
    http_method_names = ['get']
    serializer_class = serializers.ReadGradeSerializer

    def get_queryset(self):
        try:
            student = models.Student.objects.get(user_id=self.kwargs['students_pk'])
        except models.Student.DoesNotExist:
            return Response({'error': 'Student does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return models.Grade.objects.filter(student_id=student.user.id).select_related('student', 'school_year', 'semester', 'course', 'section')
        

class TeacherTeachGradeViewSet(ModelViewSet):
    http_method_names = ['get']
    serializer_class = serializers.ReadGradeSerializer

    def get_queryset(self):
        teacher_id = self.kwargs['teachers_pk']
        teach_id = self.kwargs['teaches_pk']

        teacher = self.get_teacher(teacher_id)
        teach_id = self.get_teach_id(teach_id)

        teach = teacher.teaches.filter(id=teach_id).select_related('teacher', 'school_year', 'semester', 'course', 'section').first()
        return models.Grade.objects.filter(course_id=teach.course.id, section_id=teach.section.id, 
                                           semester_id=teach.semester.id).\
                                            select_related('school_year', 'semester', 'student', 'course', 'section')

    def get_teacher(self, teacher_id):
        try:
            teacher = models.Teacher.objects.get(user_id=teacher_id)
        except models.Teacher.DoesNotExist:
            return Response({'error': 'Teacher does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return teacher

    def get_teach_id(self, teach_id):
        try:
            teach_id = models.Teach.objects.get(id=teach_id).id
        except models.Teach.DoesNotExist:
            return Response({'error': 'Record does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return teach_id
    

class StudentEnrollmentSchoolYearViewSet(ModelViewSet):
    """
    Returns all years a student has been in school which is meant to 
    fetch his/her grades for the selected school year and the semester.
    """
    http_method_names = ['get']
    serializer_class = serializers.SchoolYearSemesterSerializer

    def get_queryset(self):
        try:
            id = models.Student.objects.get(user_id=self.kwargs['students_pk']).user.id
        except models.Student.DoesNotExist:
            return Response({'error': 'Student does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        enrollments = models.Enrollment.objects.filter(student_id=id).\
            select_related('student', 'course', 'section', 'school_year', 'semester')
   
        school_year_ids = set()

        for enrollment in enrollments:
            school_year_ids.add(enrollment.school_year.id)

        return models.SchoolYear.objects.filter(id__in=list(school_year_ids)).prefetch_related('semesters')


class StudentSemesterGradeViewSet(ModelViewSet):
    """
    Takes a student_id, school_year_id, semester_id and returns the grades. 
    Only GET method is allowed.
    """
    http_method_names = ['get']
    serializer_class = serializers.ReadGradeSerializer

    def get_queryset(self):
        student_id = self.kwargs['students_pk']
        school_year_id = self.kwargs['school_years_pk']
        semester_id = self.kwargs['semesters_pk']
        try:
            models.Student.objects.get(user_id=student_id)
        except models.Student.DoesNotExist:
            return Response({'error': 'Student does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            models.SchoolYear.objects.get(id=school_year_id)
        except models.SchoolYear.DoesNotExist:
            return Response({'error': 'School year does not exist'}, status=status.HTTP_404_NOT_FOUND)
        try:
            models.Semester.objects.get(id=semester_id)
        except models.Semester.DoesNotExist:
            return Response({'error': 'Semester does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        grades = models.Grade.objects.filter(
            student_id=student_id, school_year_id=school_year_id, semester_id=semester_id)
        
        return grades
    

class FakeSchoolYearViewSet(ModelViewSet):
    """
    Just for accessing the school_year_id in the route for filtering a 
    student grades based on the school year. See: StudentSemesterGradeViewSet
    """
    pass
    

class FakeSemesterViewSet(ModelViewSet):
    """
    Just for accessing the semester_id in the route for filtering a 
    student grades based on the semester. See: StudentSemesterGradeViewSet
    """
    pass
    

