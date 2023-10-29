from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
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
        .select_related('departmentaddress').all()
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
