from rest_framework.viewsets import ModelViewSet
from . import models, serializers, permissions


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

class SemesterViewSet(ModelViewSet):
    queryset = models.Semester.objects.select_related('school_year').prefetch_related('courses').all()
    serializer_class = serializers.SemesterSerializer