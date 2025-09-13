from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .models import Course, Enrollment, CourseBlock, Resource
from .serializers import CourseSerializer, ResourceSerializer, CourseCreateSerializer

# -----------------------
# 🔒 Custom Permissions
# -----------------------
class IsStudent(permissions.BasePermission):
    message = "You must be a student to access this endpoint."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"

class IsTeacher(permissions.BasePermission):
    message = "You must be a teacher to access this endpoint."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"

class IsAdmin(permissions.BasePermission):
    message = "You must be an admin to access this endpoint."
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

# -----------------------
# 👩‍🎓 Student Views
# -----------------------
class StudentCourseListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user).select_related("course")
        data = [
            {
                "id": e.course.id,
                "title": e.course.title,
                "description": e.course.description,
                "duration": e.course.duration,
                "level": e.course.level,
                "progress": getattr(e, "progress", 0),
                "status": "Completed" if e.completed else "In Progress",
            }
            for e in enrollments
        ]
        return Response(data, status=status.HTTP_200_OK)

class StudentCourseDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get(self, request, course_id):
        enrollment = get_object_or_404(Enrollment, student=request.user, course_id=course_id)
        serializer = CourseSerializer(enrollment.course)
        return Response(serializer.data, status=status.HTTP_200_OK)

# -----------------------
# 👨‍🏫 Teacher Views
# -----------------------
class TeacherCourseListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request):
        # Filtrar por campo teacher, no created_by
        courses = Course.objects.filter(teacher=request.user)
        data = []
        for course in courses:
            students = Enrollment.objects.filter(course=course)
            data.append({
                "id": course.id,
                "title": course.title,
                "duration": course.duration,  # no duration_weeks
                "level": course.level,
                "students": [
                    {
                        "student_id": s.student.id,
                        "student_name": s.student.username,
                        "completed": s.completed,
                        "merit_points": s.merit_points
                    } for s in students
                ]
            })
        return Response(data, status=status.HTTP_200_OK)

# -----------------------
# 🛠 Admin Course Creation
# -----------------------
class AdminCourseCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = CourseCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)  # Admin que crea
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------
# 📚 Resource Upload (Teacher)
# -----------------------
class AddResourceView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def post(self, request, course_id, week_number):
        block = get_object_or_404(CourseBlock, course_id=course_id, week_number=week_number)
        title = request.data.get("title")
        file = request.FILES.get("file")
        if not title or not file:
            return Response({"error": "title and file required"}, status=status.HTTP_400_BAD_REQUEST)
        resource = Resource.objects.create(block=block, uploaded_by=request.user, title=title, file=file)
        serializer = ResourceSerializer(resource)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 👨‍🏫 Detalle de curso para profesores
class TeacherCourseDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get(self, request, course_id):
        # Validamos que el curso le pertenezca al profesor
        course = get_object_or_404(Course, id=course_id, teacher=request.user)
        serializer = CourseSerializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
