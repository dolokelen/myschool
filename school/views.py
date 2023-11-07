from django.db import transaction
from django.contrib.auth.models import Group, Permission
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from core.models import User
from core import serializers as core_serializers
from . import models, serializers, permissions, filters


class SchoolYearViewSet(ModelViewSet):
    queryset = models.SchoolYear.objects.order_by('-year')
    serializer_class = serializers.SchoolYearSerializer
    # permission_classes = [permissions.FullDjangoModelPermissions]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.ReadModelPermission()]
        if self.request.method == 'POST':
            return [permissions.CreateModelPermission()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.UpdateModelPermission()]
        if self.request.method == 'DELETE':
            return [permissions.DeleteModelPermission()]


class DepartmentViewSet(ModelViewSet):
    queryset = models.Department.objects.prefetch_related('courses')\
        .select_related('departmentaddress').prefetch_related('departmentcontact').all()
    serializer_class = serializers.DepartmentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.ReadModelPermission()]
        if self.request.method == 'POST':
            return [permissions.CreateModelPermission()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.UpdateModelPermission()]
        if self.request.method == 'DELETE':
            return [permissions.DeleteModelPermission()]


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


class CourseViewSet(ModelViewSet):
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

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.ReadModelPermission()]
        if self.request.method == 'POST':
            return [permissions.CreateModelPermission()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.UpdateModelPermission()]
        if self.request.method == 'DELETE':
            return [permissions.DeleteModelPermission()]


class SemesterViewSet(ModelViewSet):
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

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.ReadModelPermission()]
        if self.request.method == 'POST':
            return [permissions.CreateModelPermission()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.UpdateModelPermission()]
        if self.request.method == 'DELETE':
            return [permissions.DeleteModelPermission()]


class BuildingViewSet(ModelViewSet):
    queryset = models.Building.objects.select_related('buildingaddress').all()
    serializer_class = serializers.BuildingSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.ReadModelPermission()]
        if self.request.method == 'POST':
            return [permissions.CreateModelPermission()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.UpdateModelPermission()]
        if self.request.method == 'DELETE':
            return [permissions.DeleteModelPermission()]


class BuildingAddressViewSet(ModelViewSet):
    serializer_class = serializers.BuildingAddressSerializer

    def get_queryset(self):
        building_address = models.BuildingAddress.objects.filter(
            building_id=self.kwargs['buildings_pk'])

        return building_address

    def get_serializer_context(self):
        return {'building_id': self.kwargs['buildings_pk']}


class OfficeViewSet(ModelViewSet):
    queryset = models.Office.objects.select_related('building').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadOfficeSerializer
        return serializers.OfficeSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.ReadModelPermission()]
        if self.request.method == 'POST':
            return [permissions.CreateModelPermission()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.UpdateModelPermission()]
        if self.request.method == 'DELETE':
            return [permissions.DeleteModelPermission()]


class EmployeeViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = models.Employee.objects.select_related('user').select_related(
        'office').select_related('department').select_related('supervisor')\
            .select_related('employeeaddress').all()
    # serializer_class = serializers.EmployeeSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadEmployeeSerializer
        if self.request.method == 'PATCH':
            return serializers.EmployeeUpdateSerializer
        return serializers.EmployeeSerializer

    @transaction.atomic()
    def partial_update(self, request, *args, **kwargs):
        user_data = self.request.data.pop('user', None)
        user_instance = self.update_user(user_data, kwargs['pk'])

        if user_instance is None:
            return Response({'user': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

        # Use the get_serializer when you're using form at the frontend and
        # Delete the EmployeeUpdateSerializer b/c the form will have multpart
        # which will handle files encoding correctly.
        employee_instance = self.get_object()
        # serializer = self.get_serializer(employee_instance, data=request.data, partial=True)
        serializer = serializers.EmployeeUpdateSerializer(
            employee_instance, data=request.data, partial=True)
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

    def create(self, request, *args, **kwargs):
        supervisor = self.request.data.get('supervisor', None)

        if supervisor == '0':
            self.request.data['supervisor'] = None

        return super().create(request, *args, **kwargs)


class EmployeeAddressViewSet(ModelViewSet):
    queryset = models.EmployeeAddress.objects.all()
    serializer_class = serializers.EmployeeAddressSerializer

