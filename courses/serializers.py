from rest_framework import serializers
from .models import Course, CourseBlock, Resource, Enrollment

# -----------------------
# 🔹 Resource Serializer
# -----------------------
class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "title", "file", "uploaded_at"]


# -----------------------
# 🔹 CourseBlock Serializer
# Desbloqueo secuencial
# -----------------------
class CourseBlockSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = CourseBlock
        fields = ["week_number", "title", "description", "resources", "status"]

    def get_status(self, block):
        # Obtenemos al estudiante desde el contexto
        student = self.context.get("student")
        if not student:
            return "locked"

        # Obtenemos la inscripción del estudiante en el curso
        enrollment = Enrollment.objects.filter(student=student, course=block.course).first()
        if not enrollment:
            return "locked"

        # Contamos las semanas completadas (puedes almacenar completed_weeks en el modelo Enrollment)
        completed_weeks = getattr(enrollment, "completed_weeks", 0)

        if block.week_number <= completed_weeks:
            return "completed"
        elif block.week_number == completed_weeks + 1:
            return "current"
        else:
            return "locked"


# -----------------------
# 🔹 Course Serializer
# -----------------------
class CourseSerializer(serializers.ModelSerializer):
    blocks = CourseBlockSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)  # 👈 nombre del profesor

    class Meta:
        model = Course
        fields = ["id", "title", "description", "duration", "level", "blocks", "teacher_name"]


# -----------------------
# 🔹 Course Create Serializer (Admin)
# -----------------------
class CourseCreateSerializer(serializers.ModelSerializer):
    """
    Serializer específico para crear cursos desde el Admin.
    No expone los bloques ni recursos, solo lo básico.
    """
    class Meta:
        model = Course
        fields = ["id", "title", "description", "duration", "level"]
