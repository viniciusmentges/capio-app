import hashlib
from typing import Dict, Any
from django.db import transaction
from services.bible.normalization import NormalizationService
from apps.bible.models import PassageExplanation, BiblePassage
from apps.ai_core.models import AIRequest, GeneratedResponse
from services.ai import get_ai_service
from services.filters.content_filter import ContentFilter, FilterAction
from services.exceptions import ContentBlockedException

class BibleService:
    @staticmethod
    def _display_reference(reference: str) -> str:
        return reference.title()

    @staticmethod
    def _validate_and_truncate_field(text: str, max_length: int, fallback_text: str) -> str:
        if not text:
            return fallback_text
            
        length = len(text)
        # Só usamos o fallback se o conteúdo estiver absurdamente fora do padrão (proteção contra loops da IA)
        if length > max_length * 2.0:
            return fallback_text
            
        if length > max_length:
            return text[:max_length-3] + "..."
            
        return text

    @classmethod
    def _get_fallback_response(cls, ref_display: str) -> Dict[str, str]:
        return {
            "simple_explanation": "Estamos em oração e reflexão sobre esta passagem...",
            "biblical_context": "O contexto sagrado está sendo preparado para você...",
            "practical_application": "",
            "spiritual_reflection": "",
            "optional_prayer": "",
            "scripture_text": "A Palavra está sendo acolhida. Por favor, tente novamente em um instante."
        }



    @classmethod
    @transaction.atomic
    def explain(cls, reference: str, user) -> Dict[str, Any]:
        # 1. Normalização Canônica
        can_id, book, chap, verses = NormalizationService.normalize(reference)
        ref_display = cls._display_reference(reference)

        # 2. Verificar se a Palavra já existe
        bible_passage = BiblePassage.objects.filter(canonical_id=can_id).first()
        
        # 3. Se a Palavra existe, verificar se existe explicação
        if bible_passage:
            explanation = PassageExplanation.objects.filter(passage=bible_passage).first()
            if explanation:
                GeneratedResponse.objects.create(
                    response_type='BIBLE',
                    user=user,
                    content_ref_id=explanation.id,
                    filter_status='clean',
                    metadata={"cached": True, "source": "foundation"}
                )
                return {
                    "reference_display": explanation.reference_display,
                    "scripture_text": bible_passage.text_original,
                    "simple_explanation": explanation.simple_explanation,
                    "biblical_context": explanation.biblical_context,
                    "practical_application": explanation.practical_application,
                    "spiritual_reflection": explanation.spiritual_reflection,
                    "optional_prayer": explanation.optional_prayer,
                    "ai_generated": explanation.ai_generated,
                    "cached": True
                }

        # 4. Filtro de Entrada
        filter_res = ContentFilter.check_input(can_id)
        if filter_res.action == FilterAction.HARD_BLOCK:
            raise ContentBlockedException(category=filter_res.category)

        # 5. Chamada de IA
        ai_service = get_ai_service()
        input_hash = hashlib.sha256(can_id.encode()).hexdigest()
        
        ai_request = AIRequest.objects.create(
            request_type='bible',
            input_hash=input_hash,
            input_data={"canonical_id": can_id, "reference_display": ref_display},
            flagged_for_review=(filter_res.action == FilterAction.SOFT_FLAG),
            status='pending'
        )

        ai_response = ai_service.explain_passage(can_id, ref_display)
        fallback = cls._get_fallback_response(ref_display)
        
        # 6. Validação e Truncamento
        simple_explanation = cls._validate_and_truncate_field(ai_response.get("simple_explanation", ""), 900, fallback["simple_explanation"])
        biblical_context = cls._validate_and_truncate_field(ai_response.get("biblical_context", ""), 600, fallback["biblical_context"])
        practical_application = cls._validate_and_truncate_field(ai_response.get("practical_application", ""), 600, fallback["practical_application"])
        spiritual_reflection = cls._validate_and_truncate_field(ai_response.get("spiritual_reflection", ""), 500, fallback["spiritual_reflection"])
        optional_prayer = cls._validate_and_truncate_field(ai_response.get("optional_prayer", ""), 400, fallback["optional_prayer"])
        scripture_text = ai_response.get("scripture_text") or fallback["scripture_text"]

        # 7. Filtro de Saída
        ai_text_combined = f"{simple_explanation} {biblical_context} {practical_application} {spiritual_reflection} {optional_prayer}"
        out_filter_res = ContentFilter.check_output(ai_text_combined)
        
        if out_filter_res.action == FilterAction.HARD_BLOCK:
            ai_request.status = 'blocked'
            ai_request.save()
            raise ContentBlockedException(category=out_filter_res.category)
            
        ai_request.status = 'success'
        ai_request.output_data = ai_response
        ai_request.save()

        # 8. Salvar ou Atualizar BiblePassage (A Palavra Pura)
        if not bible_passage:
            bible_passage = BiblePassage.objects.create(
                canonical_id=can_id,
                book_name=book,
                chapter=chap,
                verses=verses,
                text_original=scripture_text,
                translation="NVI",
                language="pt"
            )

        # 9. Salvar PassageExplanation
        explanation = PassageExplanation.objects.create(
            passage=bible_passage,
            reference_normalized=can_id,
            reference_display=ref_display,
            simple_explanation=simple_explanation,
            biblical_context=biblical_context,
            practical_application=practical_application,
            spiritual_reflection=spiritual_reflection,
            optional_prayer=optional_prayer,
            ai_generated=ai_response.get("ai_generated", True)
        )

        # 10. Salvar GeneratedResponse
        GeneratedResponse.objects.create(
            response_type='BIBLE',
            user=user,
            ai_request=ai_request,
            content_ref_id=explanation.id,
            filter_status='clean'
        )

        return {
            "reference_display": explanation.reference_display,
            "scripture_text": bible_passage.text_original,
            "simple_explanation": explanation.simple_explanation,
            "biblical_context": explanation.biblical_context,
            "practical_application": explanation.practical_application,
            "spiritual_reflection": explanation.spiritual_reflection,
            "optional_prayer": explanation.optional_prayer,
            "ai_generated": explanation.ai_generated,
            "cached": False
        }

