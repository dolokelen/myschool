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
departments_router.register('address', views.DepartmentAddressViewSet, basename='department-address')
departments_router.register('contacts', views.DepartmentContactViewSet, basename='department-contacts')

building_router = routers.NestedDefaultRouter(router, 'buildings', lookup='buildings')
building_router.register('address', views.BuildingAddressViewSet, basename='building-address')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(departments_router.urls)),
    path("", include(building_router.urls))

]
