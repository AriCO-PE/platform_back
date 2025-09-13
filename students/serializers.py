from rest_framework import serializers
from django.utils.timezone import localtime
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# -------------------------------
# Serializers de Usuario
# -------------------------------
class UserPublicSerializer(serializers.ModelSerializer):
    ranking = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "aura",
            "specialty",
            "ranking",
            "member_since",
            "full_name",
        ]

    def get_ranking(self, obj):
        if obj.aura is None:
            return None
        users = User.objects.order_by("-aura").values_list("id", flat=True)
        try:
            return list(users).index(obj.id) + 1
        except ValueError:
            return None

    def get_member_since(self, obj):
        if getattr(obj, "joined_at", None):
            return localtime(obj.joined_at).strftime("%d-%m-%Y")
        return None

    def get_full_name(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return obj.username


class UserFullSerializer(serializers.ModelSerializer):
    ranking = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "aura",
            "specialty",
            "experience_years",
            "verified",
            "hourly_rate",
            "ranking",
            "member_since",
            "birthday",
        ]

    def get_ranking(self, obj):
        if obj.aura is None:
            return None
        users = User.objects.order_by("-aura").values_list("id", flat=True)
        try:
            return list(users).index(obj.id) + 1
        except ValueError:
            return None

    def get_member_since(self, obj):
        if getattr(obj, "joined_at", None):
            return localtime(obj.joined_at).strftime("%d-%m-%Y")
        return None


# -------------------------------
# Serializer JWT personalizado
# -------------------------------
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role  # <-- agrega el rol al token
        token["username"] = user.username
        token["email"] = user.email
        return token
