from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users', views.UserModelViewSet)
router.register('groups', views.GroupViewSet)
router.register('permissions', views.PermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('groups/<int:pk>/add_users/', views.GroupAddUserView.as_view()),
    path('groups/<int:pk>/remove_users/', views.GroupRemoveUserView.as_view())
]

