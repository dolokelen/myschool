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

semesters_router = routers.NestedDefaultRouter(
    router, 'semesters', lookup='semesters')
semesters_router.register(
    'documents', views.SemesterDocumentViewSet, basename='semester-documents')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(departments_router.urls)),
    path("", include(buildings_router.urls)),
    path("", include(semesters_router.urls))

]
