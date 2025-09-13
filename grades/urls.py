from django.urls import path
from .views import StudentGradesView

urlpatterns = [
    # Estudiante consulta sus cursos y notas
    path('', StudentGradesView.as_view(), name='student-grades'),
]
