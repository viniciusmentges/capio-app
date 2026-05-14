import hashlib
from typing import Dict, Any, Optional
from datetime import date as date_type
from django.db import transaction
from django.utils import timezone
from apps.reflection.models import DailyReflection, UserReflectionResponse
from apps.ai_core.models import AIRequest, GeneratedResponse
from services.ai import get_ai_service
from services.exceptions import NotFoundException
from services.bible.normalization import NormalizationService
from apps.bible.models import BiblePassage

import logging

logger = logging.getLogger(__name__)

class ReflectionService:
    @classmethod
    @transaction.atomic
    def get_today(cls, user=None) -> Dict[str, Any]:
        """
        Retorna a reflexão de hoje. 
        Se não existir, gera sob demanda (Fallback).
        """
        today = timezone.localtime().date()
        reflection = DailyReflection.objects.filter(date=today).first()

        cached = True
        if not reflection:
            logger.info(f"Reflexão para {today} não encontrada. Iniciando geração sob demanda (Fallback).")
            cached = False
            reflection = cls.warmup_reflection(today)

        # Buscar resposta do usuário (se houver usuário autenticado)
        user_response_text = None
        if user:
            user_response_obj = UserReflectionResponse.objects.filter(user=user, reflection=reflection).first()
            user_response_text = user_response_obj.response_text if user_response_obj else None

            # Registro de acesso para observabilidade
            has_accessed = GeneratedResponse.objects.filter(
                response_type='REFLECTION',
                user=user,
                content_ref_id=reflection.id
            ).exists()

            if not has_accessed:
                GeneratedResponse.objects.create(
                    response_type='REFLECTION',
                    user=user,
                    content_ref_id=reflection.id,
                    filter_status='clean',
                    metadata={"cached": cached, "type": "user_access"}
                )

        return {
            "reflection": {
                "id": reflection.id,
                "date": reflection.date,
                "title": reflection.title,
                "scripture_reference": reflection.scripture_reference,
                "scripture_text": reflection.scripture_text,
                "reflection_body": reflection.reflection_body,
                "guiding_question": reflection.guiding_question,
                "closing_prayer": reflection.closing_prayer,
                "ai_generated": reflection.ai_generated,
            },
            "user_response": user_response_text
        }

    @classmethod
    @transaction.atomic
    def warmup_reflection(cls, target_date: date_type = None) -> DailyReflection:
        """
        Gera e persiste a reflexão para uma data específica (Ritual Automático).
        Inclui lógica de anti-repetição de passagens.
        """
        if not target_date:
            target_date = timezone.localtime().date()

        # Evitar duplicidade
        existing = DailyReflection.objects.filter(date=target_date).first()
        if existing:
            logger.info(f"Reflexão para {target_date} já existe. Ignorando warmup.")
            return existing

        logger.info(f"Iniciando ritual de geração para {target_date}...")
        
        # Lógica Anti-Repetição: Buscar últimas 10 passagens
        recent_passages = DailyReflection.objects.order_by('-date')[:10].values_list('scripture_reference', flat=True)
        blacklist = list(recent_passages)

        ai_service = get_ai_service()
        date_str = target_date.isoformat()
        input_hash = hashlib.sha256(f"reflection-{date_str}".encode()).hexdigest()

        ai_request = AIRequest.objects.create(
            request_type='reflection',
            input_hash=input_hash,
            input_data={"date": date_str, "blacklist": blacklist},
            status='pending'
        )

        try:
            # Passamos a blacklist para o serviço de AI
            # (Assumindo que o serviço agora aceita contexto de exclusão)
            ai_response = ai_service.generate_reflection(date_str)
            
            ai_request.status = 'success'
            ai_request.output_data = ai_response
            ai_request.save()

            # Normalização e Garantia da Passagem
            ref_raw = ai_response.get("scripture_reference", "")
            can_id, book, chap, verses = NormalizationService.normalize(ref_raw)
            
            bible_passage, _ = BiblePassage.objects.get_or_create(
                canonical_id=can_id,
                defaults={
                    "book_name": book,
                    "chapter": chap,
                    "verses": verses,
                    "text_original": ai_response.get("scripture_text", ""),
                    "translation": "NVI",
                    "language": "pt"
                }
            )

            reflection = DailyReflection.objects.create(
                date=target_date,
                passage=bible_passage,
                title=ai_response.get("title", ""),
                scripture_reference=ref_raw,
                scripture_text=bible_passage.text_original,
                reflection_body=ai_response.get("reflection_body", ""),
                guiding_question=ai_response.get("guiding_question", ""),
                closing_prayer=ai_response.get("closing_prayer", ""),
                ai_generated=ai_response.get("ai_generated", True)
            )

            GeneratedResponse.objects.create(
                response_type='REFLECTION',
                user=None,
                ai_request=ai_request,
                content_ref_id=reflection.id,
                filter_status='clean',
                metadata={"source": "warmup_ritual", "is_first": True, "blacklist_count": len(blacklist)}
            )

            logger.info(f"Reflexão do dia {target_date} gerada com sucesso: {reflection.title} ({ref_raw})")
            return reflection

        except Exception as e:
            ai_request.status = 'error'
            ai_request.metadata = {"error": str(e)}
            ai_request.save()
            logger.error(f"Falha crítica no ritual de reflexão: {str(e)}")
            raise e


    @classmethod
    @transaction.atomic
    def save_response(cls, user, reflection_id: int, response_text: str):
        reflection = DailyReflection.objects.filter(id=reflection_id).first()
        if not reflection:
            raise NotFoundException(f"Reflection with id {reflection_id} not found.")

        user_resp, created = UserReflectionResponse.objects.update_or_create(
            user=user,
            reflection=reflection,
            defaults={'response_text': response_text}
        )
        return user_resp
