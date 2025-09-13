from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from .models import Course, CourseBlock, Resource, Enrollment

User = get_user_model()


# Form personalizado para Course
class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    # Limitar el campo teacher solo a usuarios con rol teacher
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(role='teacher'),
        required=True,
        label="Profesor asignado"
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ('title', 'teacher', 'created_by', 'duration', 'created_at')
    list_filter = ('teacher', 'level')
    search_fields = ('title', 'teacher__username')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Asigna automáticamente al admin que crea el curso
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CourseBlock)
class CourseBlockAdmin(admin.ModelAdmin):
    list_display = ('course', 'week_number', 'title')
    list_filter = ('course',)
    search_fields = ('title',)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'block', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_by', 'block')
    search_fields = ('title',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'completed', 'merit_points', 'completed_at')
    list_filter = ('course', 'completed')
    search_fields = ('student__username', 'course__title')
