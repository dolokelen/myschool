from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('groups', views.GroupViewSet)
router.register('permissions', views.PermissionViewSet)
router.register('years', views.SchoolYearViewSet)

urlpatterns = [
    path("", include(router.urls)),

    ]


