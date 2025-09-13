from rest_framework import serializers
from courses.models import Enrollment
from .models import ModuleGrade

class ModuleGradeSerializer(serializers.ModelSerializer):
    module_number = serializers.IntegerField(source="module.number", read_only=True)

    class Meta:
        model = ModuleGrade
        fields = ["module_number", "grade"]

class StudentGradeSerializer(serializers.Serializer):
    course_id = serializers.CharField()
    course_title = serializers.CharField()
    completed = serializers.BooleanField()
    modules = ModuleGradeSerializer(many=True)
