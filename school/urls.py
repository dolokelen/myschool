from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('departments', views.DepartmentViewSet)
router.register('years', views.SchoolYearViewSet)
router.register('courses', views.CourseViewSet)
router.register('semesters', views.SemesterViewSet)

departments_router = routers.NestedDefaultRouter(
    router, 'departments', lookup='departments')
departments_router.register('address', views.DepartmentAddressViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(departments_router.urls))

]
