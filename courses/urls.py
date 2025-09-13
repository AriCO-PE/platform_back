from django.urls import path
from .views import (
    StudentCourseListView, StudentCourseDetailView,
    TeacherCourseListView, AddResourceView,
    AdminCourseCreateView, TeacherCourseDetailView
)

urlpatterns = [
    # -------------------------
    # Student
    # -------------------------
    path("student/courses/", StudentCourseListView.as_view(), name="student-courses"),
    path("student/courses/<int:course_id>/", StudentCourseDetailView.as_view(), name="student-course-detail"),

    # -------------------------
    # Teacher
    # -------------------------
    path("teacher/courses/", TeacherCourseListView.as_view(), name="teacher-courses"),
    path("teacher/courses/<int:course_id>/", TeacherCourseDetailView.as_view(), name="teacher-course-detail"),
    path("teacher/courses/<int:course_id>/students/", TeacherCourseListView.as_view(), name="teacher-course-students"),
    path("teacher/courses/<int:course_id>/add-points/", TeacherCourseListView.as_view(), name="teacher-course-add-points"),
    path("teacher/courses/<int:course_id>/finalize/", TeacherCourseListView.as_view(), name="teacher-course-finalize"),



    # -------------------------
    # Resources (Teacher)
    # -------------------------
    path(
        "teacher/courses/<int:course_id>/blocks/<int:week_number>/add-resource/",
        AddResourceView.as_view(),
        name="add-resource",
    ),

    # -------------------------
    # Admin
    # -------------------------
    path("admin/courses/create/", AdminCourseCreateView.as_view(), name="admin-create-course"),
]
