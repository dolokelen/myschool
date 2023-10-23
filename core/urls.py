from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet)
router.register('groups', views.GroupViewSet)
router.register('permissions', views.PermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user_groups/<int:pk>/', views.ListUserGroups.as_view()),

    path('index', views.index, name='index')
]

