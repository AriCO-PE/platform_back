from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from courses.models import Enrollment, Module
from .models import ModuleGrade
from .serializers import StudentGradeSerializer

class StudentGradesView(APIView):
    """
    GET /api/grades/?student_id=<id>
    Muestra los cursos y notas de módulos del estudiante.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get("student_id")
        
        if not student_id:
            return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollments = Enrollment.objects.filter(student_id=student_id)
        data = []

        for enroll in enrollments:
            # Crear notas si no existen
            for module in enroll.course.modules.all():
                ModuleGrade.objects.get_or_create(enrollment=enroll, module=module)

            # Traer las notas de los módulos
            module_grades = ModuleGrade.objects.filter(enrollment=enroll)

            data.append({
                "course_id": str(enroll.course.id),
                "course_title": enroll.course.title,
                "completed": enroll.completed,
                "modules": module_grades
            })

        serializer = StudentGradeSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
