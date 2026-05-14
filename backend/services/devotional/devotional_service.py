from services.exceptions import NotFoundException
import hashlib
import random
import logging
from typing import Dict, Any
from django.db import transaction
from django.db.models import Max, Q
from apps.devotional.models import Emotion, DevotionalContent, UserDevotional
from apps.ai_core.models import AIRequest, GeneratedResponse
from services.ai import get_ai_service
from services.bible.normalization import NormalizationService
from apps.bible.models import BiblePassage

logger = logging.getLogger(__name__)

class DevotionalService:
    @classmethod
    @transaction.atomic
    def get_for_emotion(cls, emotion_slug: str, user) -> Dict[str, Any]:
        emotion = Emotion.objects.filter(slug=emotion_slug).first()
        if not emotion:
            raise NotFoundException(f"Emotion with slug '{emotion_slug}' not found.")

        # 1. Tentar buscar da Biblioteca (Excluindo lidos pelo usuário)
        user_history = UserDevotional.objects.filter(user=user).values_list('content_id', flat=True)
        available_contents = DevotionalContent.objects.filter(
            emotion=emotion, 
            is_active=True
        ).exclude(id__in=user_history)

        if available_contents.exists():
            content = random.choice(list(available_contents))
            UserDevotional.objects.create(user=user, content=content)
            GeneratedResponse.objects.create(
                response_type='DEVOTIONAL',
                user=user,
                content_ref_id=content.id,
                filter_status='clean',
                metadata={"cached": True, "source": "foundation_library"}
            )
            return {
                "title": content.title,
                "scripture_reference": content.scripture_reference,
                "scripture_text": content.scripture_text,
                "reflection": content.reflection,
                "practical_application": content.practical_application,
                "guiding_question": content.guiding_question,
                "prayer": content.prayer,
                "ai_generated": content.ai_generated,
                "cached": True
            }

        # 2. Se não houver inéditos, gerar novo (Expansão Orgânica)
        ai_service = get_ai_service()
        input_hash = hashlib.sha256(emotion.name.encode()).hexdigest()

        ai_request = AIRequest.objects.create(
            request_type='devotional',
            input_hash=input_hash,
            input_data={"emotion_name": emotion.name},
            status='pending'
        )

        ai_response = ai_service.devotional_for_emotion(emotion.name)

        ai_request.status = 'success'
        ai_request.output_data = ai_response
        ai_request.save()

        # 3. Normalização e Vínculo com a Palavra
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

        # 4. Salvar na Biblioteca Permanente
        content = DevotionalContent.objects.create(
            emotion=emotion,
            passage=bible_passage,
            title=ai_response.get("title", ""),
            scripture_reference=ref_raw,
            scripture_text=bible_passage.text_original,
            reflection=ai_response.get("reflection", ""),
            practical_application=ai_response.get("practical_application", ""),
            guiding_question=ai_response.get("guiding_question", ""),
            prayer=ai_response.get("prayer", ""),
            is_active=True,
            ai_generated=ai_response.get("ai_generated", True)
        )

        UserDevotional.objects.create(user=user, content=content)

        GeneratedResponse.objects.create(
            response_type='DEVOTIONAL',
            user=user,
            ai_request=ai_request,
            content_ref_id=content.id,
            filter_status='clean',
            metadata={"cached": False, "source": "editorial_motor", "organic_growth": True}
        )

        return {
            "title": content.title,
            "scripture_reference": content.scripture_reference,
            "scripture_text": content.scripture_text,
            "reflection": content.reflection,
            "practical_application": content.practical_application,
            "guiding_question": content.guiding_question,
            "prayer": content.prayer,
            "ai_generated": content.ai_generated,
            "cached": False
        }

