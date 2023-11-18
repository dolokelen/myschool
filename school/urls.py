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
router.register('employee-profile',
                views.EmployeeProfileViewSet, basename='profile')
router.register('teachers', views.TeacherViewSet)
router.register('teacher-profile', views.TeacherProfileViewSet,
                basename='profile')
router.register('majors', views.MajorViewSet)
router.register('students', views.StudentViewSet)
router.register('student-profile', views.StudentProfileViewSet,
                basename='profile')
router.register('classrooms', views.ClassRoomViewSet)
router.register('classtimes', views.ClassTimeViewSet)
router.register('sections', views.SectionViewSet)
router.register('current-semester-courses',
                views.CurrentSemesterCourseViewSet, basename='current-semester-courses')

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

sections_router = routers.NestedDefaultRouter(
    router, 'sections', lookup='sections')
sections_router.register(
    'attendances', views.AttendanceViewSet, basename='section-attendances')

students_router = routers.NestedDefaultRouter(
    router, 'students', lookup='students')
students_router.register(
    'enrollments', views.EnrollmentViewSet, basename='student-entrollments')
students_router.register('eligible-courses', views.StudentEligibleCourseViewSet, basename='student-enrolls')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(departments_router.urls)),
    path("", include(buildings_router.urls)),
    path("", include(sections_router.urls)),
    path("", include(students_router.urls)),

]
