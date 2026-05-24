from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import timedelta
from collections import Counter

from .models import UserReflectionResponse, DailyReflection, EditorialFragment, ContemplativeExperience, SpiritualCollection
from .serializers import RespondRequestSerializer, UserReflectionResponseSerializer, DailyReflectionSerializer
from services.reflection.reflection_service import ReflectionService
from services.exceptions import NotFoundException
from apps.ai_core.models import GeneratedResponse

class TodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            res = ReflectionService.get_today(request.user)
            # Metadados de ritual e preparação contemplativos
            res["metadata"] = {
                "reflection_prepared": True,
                "preparation_microcopy": "A reflexão de hoje já está preparada.",
                "monastic_whisper": "Há algo reservado para este dia."
            }
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RespondView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RespondRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
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

class NightView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            today_res = ReflectionService.get_today(request.user)
            reflection = DailyReflection.objects.get(id=today_res['reflection']['id'])
            
            # Garantir formato curto, apenas o fragmento e a oração curta para o eco do fim do dia
            return Response({
                "id": reflection.id,
                "date": reflection.date,
                "title": reflection.title,
                "scripture_reference": reflection.scripture_reference,
                "share_quote": reflection.share_quote,
                "closing_prayer": reflection.closing_prayer,
                "theme_key": reflection.theme_key,
                "emotional_theme": reflection.emotional_theme
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiturgicalArchiveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            reflections = DailyReflection.objects.all().order_by('-date')[:7]
            serializer = DailyReflectionSerializer(reflections, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SpiritualJourneyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            thirty_days_ago = timezone.localtime() - timedelta(days=30)
            
            # 1. Obter reflexões lidas
            read_reflection_ids = GeneratedResponse.objects.filter(
                user=request.user,
                response_type='REFLECTION',
                created_at__gte=thirty_days_ago
            ).values_list('content_ref_id', flat=True)
            
            read_reflections = DailyReflection.objects.filter(id__in=read_reflection_ids)
            
            # 2. Obter devocionais lidos
            from apps.devotional.models import UserDevotional
            accessed_devotionals = UserDevotional.objects.filter(
                user=request.user,
                accessed_at__gte=thirty_days_ago
            ).select_related('content')
            
            # 3. Contar eixos temáticos e emoções
            theme_keys = []
            for ref in read_reflections:
                if ref.theme_key:
                    theme_keys.append(ref.theme_key)
            for acc in accessed_devotionals:
                if acc.content.emotional_theme:
                    theme_keys.append(acc.content.emotional_theme)
                    
            # 4. Mapear termos pastorais
            theme_translation = {
                "contemplacao": "silêncio e quietude",
                "coragem": "coragem ativa",
                "identidade": "sua identidade filial",
                "obediencia": "obediência simples",
                "perdao": "o perdão libertador",
                "vocacao": "vocação no comum",
                "esperanca": "esperança viva",
                "graca": "misericórdia e graça",
                "transformacao": "maturidade paciente",
                "comunidade": "serviço ao próximo",
                "tentacao": "resistência vigilante",
                "alegria": "gratidão sincera",
                "sofrimento": "redenção na dor",
                "tensao_espiritual": "tensões da alma",
            }
            
            # Obter os 2 temas mais frequentes
            theme_counts = Counter(theme_keys)
            top_themes = [t[0] for t in theme_counts.most_common(2)]
            
            pastoral_themes = []
            for t in top_themes:
                translated = theme_translation.get(t.lower())
                if translated:
                    pastoral_themes.append(translated)
                    
            # Fallback se não houver dados suficientes para manter a sonoridade pastoral
            if len(pastoral_themes) < 2:
                fallbacks = ["esperança viva", "silêncio e quietude"]
                for f in fallbacks:
                    if f not in pastoral_themes:
                        pastoral_themes.append(f)
                    if len(pastoral_themes) == 2:
                        break
                        
            journey_text = (
                f"Nas últimas semanas, seus momentos de pausa e leitura caminharam próximos a temas de "
                f"{pastoral_themes[0]} e {pastoral_themes[1]}. Que o Senhor continue guiando seus passos no silêncio."
            )
            
            return Response({
                "journey_text": journey_text,
                "top_themes": top_themes,
                "read_count": len(read_reflection_ids) + accessed_devotionals.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": "Internal server error.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

