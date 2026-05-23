from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserReflectionResponse
from .serializers import RespondRequestSerializer, UserReflectionResponseSerializer
from services.reflection.reflection_service import ReflectionService
from services.exceptions import NotFoundException

class TodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            res = ReflectionService.get_today(request.user)
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RespondView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RespondRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # To save response, we need the reflection id.
                # get_today ensures we have today's reflection created.
                today_res = ReflectionService.get_today(request.user)
                reflection_id = today_res['reflection']['id']

                ReflectionService.save_response(
                    user=request.user,
                    reflection_id=reflection_id,
                    response_text=serializer.validated_data['response_text']
                )
                return Response({"status": "success"}, status=status.HTTP_201_CREATED)
            except NotFoundException as e:
                return Response({"error": "not_found", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            responses = UserReflectionResponse.objects.filter(user=request.user).select_related('reflection').order_by('-created_at')
            serializer = UserReflectionResponseSerializer(responses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import DailyReflection
from .serializers import DailyReflectionSerializer
from rest_framework.permissions import AllowAny

class PublicReflectionDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            reflection = DailyReflection.objects.get(pk=pk)
            serializer = DailyReflectionSerializer(reflection)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DailyReflection.DoesNotExist:
            return Response({"error": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.conf import settings
from services.reflection.editorial_analytics import (
    get_theme_distribution,
    get_emotional_theme_frequency,
    get_scripture_coverage,
    get_saturation_alerts,
    get_editorial_timeline,
    generate_editorial_report
)

class EditorialInsightsView(APIView):
    """
    Endpoint de observabilidade e curadoria de inteligência semântica.
    Apenas acessível a equipe staff, superusuários ou em ambiente de desenvolvimento (DEBUG).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser or settings.DEBUG):
            return Response(
                {"error": "forbidden", "message": "Apenas curadores editoriais têm acesso a estes dados."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        try:
            days = int(request.query_params.get('days', 30))
        except ValueError:
            days = 30
            
        try:
            timeline = get_editorial_timeline(days)
            coverage = get_scripture_coverage(days)
            alerts = get_saturation_alerts(days)
            distribution = get_theme_distribution(days)
            emotional = get_emotional_theme_frequency(days)
            report = generate_editorial_report(days)
            
            return Response({
                "theme_distribution": distribution,
                "emotional_distribution": emotional,
                "scripture_coverage": coverage,
                "saturation_alerts": alerts,
                "timeline": timeline,
                "report": report
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "Internal server error.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
