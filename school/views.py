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
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer

class CourseViewSet(ModelViewSet):
    queryset = models.Course.objects.select_related('department').all()
    serializer_class = serializers.CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = filters.CourseFilter
    search_fields = ['code', 'title']
    ordering_fields = ['price_per_credit', 'credit', 'additional_fee']

class SemesterViewSet(ModelViewSet):
    queryset = models.Semester.objects.select_related('school_year').prefetch_related('courses').all()
    serializer_class = serializers.SemesterSerializer