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
router.register('current-semester-courses',views.CurrentSemesterCourseViewSet, basename='current-semester-courses')
router.register('only-courses-with-sections',views.OnlyCourseWithSectionViewSet, basename='semester-courses-sections')
router.register('teach-update', views.TeachUpdate)

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
sections_router.register('current-semester-section-enrollments',
                views.CurrentSemesterSectionEnrollmentViewSet, basename='curr-sem-sec-enrollments')
sections_router.register('classroom',
                views.SectionClassroomViewSet, basename='section-classroom')
sections_router.register('classtime',
                views.SectionClasstimeViewSet, basename='section-classtime')

students_router = routers.NestedDefaultRouter(
    router, 'students', lookup='students')
students_router.register(
    'enrollments', views.EnrollmentViewSet, basename='student-entrollments')
students_router.register('eligible-courses', views.StudentEligibleCourseViewSet, basename='student-enrolls')

teachers_router = routers.NestedDefaultRouter(router, 'teachers', lookup='teachers')
teachers_router.register('teaches', views.TeachAndSectionEnrollmentViewSet, basename='teacher-teaches')
teachers_router.register('sections', views.TeacherAssignSectionViewSet, basename='teacher-sections')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(departments_router.urls)),
    path("", include(buildings_router.urls)),
    path("", include(sections_router.urls)),
    path("", include(students_router.urls)),
    path("", include(teachers_router.urls)),

]
