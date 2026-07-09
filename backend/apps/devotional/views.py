from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Emotion, UserDevotional
from .serializers import EmotionSerializer, DevotionalRequestSerializer, UserDevotionalSerializer
from services.devotional.devotional_service import DevotionalService
from services.exceptions import NotFoundException

class EmotionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        emotions = Emotion.objects.all()
        serializer = EmotionSerializer(emotions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.throttling import UserRateThrottle

class DevotionalHeavyThrottle(UserRateThrottle):
    scope = 'devotional_heavy'

class DevotionalByEmotionView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [DevotionalHeavyThrottle]

    def post(self, request):
        serializer = DevotionalRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                res = DevotionalService.get_for_emotion(
                    emotion_slug=serializer.validated_data['emotion_slug'],
                    user=request.user
                )
                return Response(res, status=status.HTTP_200_OK)
            except NotFoundException as e:
                return Response({"error": "not_found", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            history = UserDevotional.objects.filter(user=request.user).select_related('content').order_by('-accessed_at')
            serializer = UserDevotionalSerializer(history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import DevotionalContent
from .serializers import DevotionalContentSerializer
from rest_framework.permissions import AllowAny

class PublicDevotionalDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, public_id):
        try:
            from django.db.models import Q
            content = DevotionalContent.objects.get(Q(is_active=True) | Q(reviewed_by_human=True), public_id=public_id)
            serializer = DevotionalContentSerializer(content)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DevotionalContent.DoesNotExist:
            return Response({"error": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication
from services.ai import get_ai_service
import logging

logger = logging.getLogger(__name__)

class EditorialDevotionalGenerateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        emotion_slug = request.data.get('emotion_slug')
        tone_or_direction = request.data.get('tone_or_direction', '')

        if not emotion_slug:
            return Response({"error": "emotion_slug_required", "message": "O slug da emoção é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            emotion = Emotion.objects.get(slug=emotion_slug)
        except Emotion.DoesNotExist:
            return Response({"error": "emotion_not_found", "message": f"Emoção '{emotion_slug}' não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Consultar banco para construir listas de exclusão antes de chamar a IA
            exc_passages, excluded_canonical_ids, exc_themes, exc_titles, semantic_cooldown = DevotionalService.build_exclusions_and_cooldown(emotion)

            logger.info(
                "[CAPIO EDITORIAL] Gerando devocional para '%s' com %d passagens excluídas, %d temas excluídos, %d títulos excluídos.",
                emotion.name, len(exc_passages), len(exc_themes), len(exc_titles)
            )
            if semantic_cooldown:
                logger.info(
                    "[CAPIO SEMANTIC AUDIT] Palavras em resfriamento para '%s': %s",
                    emotion.name, ', '.join(semantic_cooldown)
                )
            else:
                logger.info("[CAPIO SEMANTIC AUDIT] Sem palavras em resfriamento para '%s'.", emotion.name)

            ai_service = get_ai_service()

            res = ai_service.editorial_generate_devotional(
                emotion_name=emotion.name,
                tone_or_direction=tone_or_direction,
                excluded_passages=exc_passages,
                excluded_themes=exc_themes,
                excluded_titles=exc_titles,
                semantic_cooldown_words=semantic_cooldown,
            )

            # Validação pós-resposta: normalizar scripture_reference e verificar canonical_id
            returned_ref = res.get('scripture_reference', '')
            if returned_ref and excluded_canonical_ids:
                duplicate_canonical_id = self._check_duplicate(returned_ref, excluded_canonical_ids)
                if duplicate_canonical_id:
                    logger.warning(
                        "[CAPIO EDITORIAL] Passagem duplicada '%s' (canonical: %s) detectada para emoção '%s'. Iniciando retry.",
                        returned_ref, duplicate_canonical_id, emotion.name
                    )
                    retry_direction = (
                        f"[ATENÇÃO EDITORIAL CRÍTICA: A passagem '{returned_ref}' JÁ EXISTE na biblioteca CAPIO para esta emoção. "
                        f"É OBRIGATÓRIO escolher uma passagem bíblica completamente diferente e um ângulo espiritual novo e distinto.]"
                    )
                    if tone_or_direction:
                        retry_direction = f"{tone_or_direction} — {retry_direction}"

                    res = ai_service.editorial_generate_devotional(
                        emotion_name=emotion.name,
                        tone_or_direction=retry_direction,
                        excluded_passages=exc_passages,
                        excluded_themes=exc_themes,
                        excluded_titles=exc_titles,
                        semantic_cooldown_words=semantic_cooldown,
                    )

                    # Segunda verificação: se ainda duplicar, retornar erro claro para o admin
                    returned_ref2 = res.get('scripture_reference', '')
                    if returned_ref2 and excluded_canonical_ids:
                        duplicate_canonical_id2 = self._check_duplicate(returned_ref2, excluded_canonical_ids)
                        if duplicate_canonical_id2:
                            logger.error(
                                "[CAPIO EDITORIAL] IA repetiu passagem duplicada '%s' após retry para emoção '%s'. Abortando.",
                                returned_ref2, emotion.name
                            )
                            return Response(
                                {
                                    "error": "duplicate_passage",
                                    "message": (
                                        "A IA tentou repetir uma passagem já usada mesmo após nova tentativa. "
                                        "Tente gerar novamente com uma direção espiritual mais específica."
                                    ),
                                },
                                status=status.HTTP_409_CONFLICT,
                            )

            # CAPIO SEMANTIC AUDIT — pós-geração
            final_ref = res.get('scripture_reference', '')
            final_quote = res.get('share_quote', '')
            logger.info(
                "[CAPIO SEMANTIC AUDIT] Passagem gerada: '%s' | Emoção: '%s'",
                final_ref, emotion.name
            )
            # Detecção heurística de paralelismo no share_quote (A→B / A'→B')
            quote_parts = [p.strip() for p in final_quote.replace('!', '.').split('.') if p.strip()]
            if len(quote_parts) >= 2:
                first_words = [p.split()[0].lower() if p.split() else '' for p in quote_parts[:2]]
                if first_words[0] and first_words[0] == first_words[1]:
                    logger.warning(
                        "[CAPIO SEMANTIC AUDIT] share_quote possivelmente paralelístico: '%s'",
                        final_quote
                    )

            from services.editorial.editor import EditorialEditorService
            res = EditorialEditorService.review_and_publish(res)

            return Response(res, status=status.HTTP_200_OK)

        except Exception as e:
            err_class = type(e).__name__
            err_msg = str(e).lower()
            is_timeout = 'timeout' in err_class.lower() or 'timeout' in err_msg or 'timed out' in err_msg
            if is_timeout:
                logger.warning("[CAPIO EDITORIAL] Timeout na chamada Anthropic para emoção '%s': %s", emotion.name, e)
                return Response(
                    {"error": "timeout", "message": "A IA demorou mais que o esperado. Tente novamente."},
                    status=status.HTTP_504_GATEWAY_TIMEOUT,
                )
            logger.error("Falha ao gerar devocional com IA no fluxo editorial: %s", e)
            return Response({"error": "generation_failed", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @staticmethod
    def _check_duplicate(scripture_reference: str, excluded_canonical_ids: set) -> str:
        """Normaliza a referência retornada pela IA e verifica se já existe na emoção. Retorna o canonical_id duplicado ou ''."""
        try:
            from services.bible.normalization import NormalizationService
            canonical_id, _, _, verses = NormalizationService.normalize(scripture_reference)
            if verses:
                canonical_id = f"{canonical_id}.{verses}"
            if canonical_id in excluded_canonical_ids:
                return canonical_id
        except Exception as err:
            logger.warning("[CAPIO EDITORIAL] Erro ao normalizar referência '%s' para validação: %s", scripture_reference, err)
        return ''


class SyncEditorialView(APIView):
    """
    Endpoint administrativo/operacional para forçar a sincronização e ativação 
    das 20 emoções e 147 devocionais no banco de dados do Django em qualquer momento.
    """
    permission_classes = []

    def get(self, request):
        from rest_framework.permissions import AllowAny
        from django.core.management import call_command
        from apps.devotional.models import Emotion, DevotionalContent
        try:
            call_command('import_editorial_staging')
            
            icons_map = {
                'ansioso': 'anxiety_icon',
                'triste': 'sad_icon',
                'medo': 'fear_icon',
                'desmotivado': 'unmotivated_icon',
                'sozinho': 'lonely_icon',
                'sem-esperanca': 'hopeless_icon',
                'direcao': 'direction_icon',
                'gratidao': 'gratitude_icon',
                'inseguro': 'insecure_icon',
                'cansado': 'tired_icon',
                'corajoso-mas-incerto': 'courageous_uncertain_icon',
                'chamado-mas-hesitante': 'called_hesitant_icon',
                'tentado': 'tempted_icon',
                'em-conflito-com-alguem': 'conflict_icon',
                'grato-mas-disperso': 'grateful_dispersed_icon',
                'disciplinado-mas-frio': 'disciplined_cold_icon',
                'culpado': 'guilty_icon',
                'raiva': 'anger_icon',
                'confuso': 'confused_icon',
                'vazio': 'empty_icon',
            }
            for slug, icon_name in icons_map.items():
                Emotion.objects.filter(slug=slug).update(icon=icon_name)
            
            all_slugs = list(icons_map.keys())
            promoted_count = DevotionalContent.objects.filter(
                emotion__slug__in=all_slugs
            ).update(is_active=True, reviewed_by_human=True)

            emotions_list = [f"{e.slug} ({e.icon})" for e in Emotion.objects.all().order_by('id')]
            return Response({
                "status": "SUCCESS",
                "message": f"Acervo editorial sincronizado! {promoted_count} devocionais ativos em {len(emotions_list)} emoções.",
                "active_devotionals_count": promoted_count,
                "emotions": emotions_list
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "ERROR",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

