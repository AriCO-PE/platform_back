from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL


class Course(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    duration = models.IntegerField(default=12, help_text="Duración en semanas")

    # Solo admin puede crear
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses_created",
    )
    # Admin puede asignar profesor
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "teacher"},
        related_name="courses_teaching",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if hasattr(self.created_by, "role") and self.created_by.role != "admin":
            raise ValidationError("Solo un administrador puede crear cursos.")

    def __str__(self):
        return f"{self.title} ({self.duration} semanas)"


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("course", "number")
        ordering = ["number"]

    def __str__(self):
        return f"{self.course.title} - Módulo {self.number}: {self.title}"


class CourseBlock(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="blocks")
    week_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("module", "week_number")
        ordering = ["week_number"]

    def clean(self):
        if self.week_number < 1 or self.week_number > 12:
            raise ValidationError("El número de semana debe estar entre 1 y 12.")

    def __str__(self):
        return f"{self.module.course.title} - Módulo {self.module.number} - Semana {self.week_number}: {self.title}"


class Resource(models.Model):
    block = models.ForeignKey(
        CourseBlock, on_delete=models.CASCADE, related_name="resources"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="resources_uploaded",
        limit_choices_to={"role": "teacher"},
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="course_resources/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.block} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "student"},
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    merit_points = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


# ---------------------------
# Signals
# ---------------------------
@receiver(post_save, sender=Course)
def create_course_structure(sender, instance, created, **kwargs):
    if created:
        modules = [
            (1, range(1, 5)),   # semanas 1-4
            (2, range(5, 9)),   # semanas 5-8
            (3, range(9, 13)),  # semanas 9-12
        ]

        for number, weeks in modules:
            module = Module.objects.create(
                course=instance,
                number=number,
                title=f"Módulo {number}",
                description=f"Contenido del módulo {number}.",
            )
            for week in weeks:
                CourseBlock.objects.create(
                    module=module,
                    week_number=week,
                    title=f"Semana {week}",
                    description=f"Contenido de la semana {week}.",
                )
