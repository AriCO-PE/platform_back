from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from .models import Course, CourseBlock, Resource, Enrollment

User = get_user_model()


# ---------------------------
# Form personalizado para Course
# ---------------------------
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


# ---------------------------
# Admin de Course
# ---------------------------
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


# ---------------------------
# Admin de CourseBlock
# ---------------------------
@admin.register(CourseBlock)
class CourseBlockAdmin(admin.ModelAdmin):
    list_display = ('get_course_title', 'week_number', 'title')
    list_filter = ('course',)
    search_fields = ('title',)

    def get_course_title(self, obj):
        return obj.course.title
    get_course_title.admin_order_field = 'course'  # Permite ordenar por curso
    get_course_title.short_description = 'Course'


# ---------------------------
# Admin de Resource
# ---------------------------
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_block_info', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_by', 'block')
    search_fields = ('title',)

    def get_block_info(self, obj):
        return f"{obj.block.course.title} - Semana {obj.block.week_number}"
    get_block_info.admin_order_field = 'block'
    get_block_info.short_description = 'Block'


# ---------------------------
# Admin de Enrollment
# ---------------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'completed', 'merit_points', 'completed_at')
    list_filter = ('course', 'completed')
    search_fields = ('student__username', 'course__title')
