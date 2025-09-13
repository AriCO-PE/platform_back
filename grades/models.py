from django.db import models
from django.conf import settings
from courses.models import Course, Module, Enrollment

User = settings.AUTH_USER_MODEL

class ModuleGrade(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="module_grades"
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE
    )
    grade = models.PositiveIntegerField(default=0)  # escala 1-5

    class Meta:
        unique_together = ("enrollment", "module")

    def clean(self):
        if self.grade < 1 or self.grade > 5:
            raise ValueError("La nota debe estar entre 1 y 5")

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.module} : {self.grade}"
