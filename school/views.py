from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
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
        .select_related('departmentaddress').prefetch_related('departmentcontact').all()
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
        'prerequisite').select_related('department').all()
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
        existing_courses = semester.courses.all()
        existing_courses_ids = existing_courses.values_list('id', flat=True)
        combined_courses = list(existing_courses_ids) + courses_to_add_ids
        semester.courses.set(combined_courses)
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadSemesterSerializer
        return serializers.SemesterSerializer


class BuildingViewSet(Permission):
    queryset = models.Building.objects.select_related('buildingaddress').all()
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

        serializer = self.get_serializer(employee_instance, data=mutable_data, partial=True)
               
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
        address_instance = models.EmployeeAddress.objects.get(employee_id=user_id)
        serializer = serializers.EmployeeAddressSerializer(address_instance, data=address_data)
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.TeacherFilter
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = models.Teacher.objects.select_related('user').select_related(
        'office').select_related('department').select_related('supervisor')\
            .select_related('teacheraddress').all()
    
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

        serializer = self.get_serializer(teacher_instance, data=mutable_data, partial=True)
               
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
        address_instance = models.TeacherAddress.objects.get(teacher_id=user_id)
        serializer = serializers.TeacherAddressSerializer(address_instance, data=address_data)
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

