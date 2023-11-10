from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('departments', views.DepartmentViewSet)
router.register('years', views.SchoolYearViewSet)
router.register('courses', views.CourseViewSet)
router.register('semesters', views.SemesterViewSet)
router.register('buildings', views.BuildingViewSet)
router.register('offices', views.OfficeViewSet)
router.register('employees', views.EmployeeViewSet)
router.register('employee-profile', views.EmployeeProfileViewSet, basename='profile')
router.register('teachers', views.TeacherViewSet)

departments_router = routers.NestedDefaultRouter(
    router, 'departments', lookup='departments')
departments_router.register(
    'address', views.DepartmentAddressViewSet, basename='department-address')
departments_router.register(
    'contacts', views.DepartmentContactViewSet, basename='department-contacts')

buildings_router = routers.NestedDefaultRouter(
    router, 'buildings', lookup='buildings')
buildings_router.register(
    'address', views.BuildingAddressViewSet, basename='building-address')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(departments_router.urls)),
    path("", include(buildings_router.urls)),

]
