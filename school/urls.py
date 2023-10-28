from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('years', views.SchoolYearViewSet)
router.register('departments', views.DepartmentViewSet)
router.register('courses', views.CourseViewSet)
router.register('semesters', views.SemesterViewSet)
router.register('address', views.AddressViewSet)

urlpatterns = [
    path("", include(router.urls)),

    ]


