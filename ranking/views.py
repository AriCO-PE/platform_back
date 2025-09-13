from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, F, Window
from django.db.models.functions import Rank
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class RankingView(APIView):
    """
    GET /api/ranking/?search=<name>
    - Devuelve:
      1. Posición del estudiante logueado (obtenido vía JWT)
      2. Ranking general ordenado por aura
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.query_params.get("search", "")

        students = User.objects.filter(role="student")

        if search_query:
            students = students.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        # Anotar ranking
        ranked_students = students.annotate(
            rank=Window(
                expression=Rank(),
                order_by=F('aura').desc()
            )
        ).order_by('-aura')

        # Preparar datos del ranking general
        ranking = [
            {
                "id": str(s.id),
                "first_name": s.first_name,
                "last_name": s.last_name,
                "aura": s.aura,
                "rank": s.rank
            }
            for s in ranked_students
        ]

        # Encontrar posición del usuario logueado
        user_rank = next((s for s in ranking if s["id"] == str(request.user.id)), None)

        return Response({
            "user_rank": user_rank,
            "ranking": ranking
        }, status=status.HTTP_200_OK)
