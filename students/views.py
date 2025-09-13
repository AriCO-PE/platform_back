from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserPublicSerializer, UserFullSerializer, MyTokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from django.db.models import F, Window
from django.db.models.functions import Rank
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


# ---------------------------
# LOGIN
# ---------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=401)

        if user.check_password(password):  # ✅ más seguro que check_password()
            refresh = MyTokenObtainPairSerializer.get_token(user)
            return Response({
                "id": str(user.id),
                "role": user.role,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=200)

        return Response({"error": "Invalid credentials"}, status=401)


# ---------------------------
# CAMBIAR CONTRASEÑA
# ---------------------------
class ChangePasswordView(APIView):
    """
    POST /api/change-password/
    Headers:
        Authorization: Bearer <access_token>
    Body:
    {
        "old_password": "OldPass1234",
        "new_password": "NewPass5678"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "Both old and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        # 🔒 Validaciones básicas (puedes mover a AUTH_PASSWORD_VALIDATORS en settings.py)
        if len(new_password) < 8:
            return Response({"error": "Password must be at least 8 characters long"}, status=status.HTTP_400_BAD_REQUEST)
        if not any(c.isupper() for c in new_password):
            return Response({"error": "Password must contain at least one uppercase letter"}, status=status.HTTP_400_BAD_REQUEST)
        if sum(c.isdigit() for c in new_password) < 4:
            return Response({"error": "Password must contain at least 4 digits"}, status=status.HTTP_400_BAD_REQUEST)

        user.password = make_password(new_password)
        user.save()

        return Response({
            "message": "Password updated successfully",
            "role": user.role,
            "id": str(user.id)
        }, status=status.HTTP_200_OK)


# ---------------------------
# LOGOUT
# ---------------------------
class LogoutView(APIView):
    """
    POST /api/logout/
    Body:
    {
        "refresh": "<refresh_token>"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Requiere 'rest_framework_simplejwt.token_blacklist' en INSTALLED_APPS
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------
# PERFIL
# ---------------------------
class ProfileView(APIView):
    """
    GET /api/users/profile/<user_id>/
    Headers:
        Authorization: Bearer <access_token>

    - Si el token corresponde al mismo user_id → perfil completo
    - Si no → perfil público
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        logged_id = None

        # Si el usuario mandó token en headers
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = AccessToken(token)
                logged_id = str(payload["user_id"])
            except Exception:
                logged_id = None

        # Buscar usuario o devolver 404
        user = get_object_or_404(User, id=user_id)

        # Calcular ranking solo si es el propio usuario
        user_rank = None
        if logged_id and str(user.id) == logged_id and user.role == "student":
            user_rank = (
                User.objects.filter(role="student")
                .annotate(rank=Window(expression=Rank(), order_by=F("aura").desc()))
                .filter(id=user.id)
                .values_list("rank", flat=True)
                .first()
            )

        # Serializar usuario
        if logged_id and str(user.id) == logged_id:
            serializer = UserFullSerializer(user)
            data = serializer.data
            data["ranking"] = user_rank
        else:
            serializer = UserPublicSerializer(user)
            data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
