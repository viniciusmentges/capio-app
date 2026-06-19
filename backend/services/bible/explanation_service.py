import hashlib
import logging
from typing import Dict, Any
import httpx
import json
from django.db import transaction
from services.bible.normalization import NormalizationService
from apps.bible.models import PassageExplanation, BiblePassage
from apps.ai_core.models import AIRequest, GeneratedResponse
from services.ai import get_ai_service
from services.filters.content_filter import ContentFilter, FilterAction
from services.exceptions import ContentBlockedException
from services.observability import capture_exception, log_event

logger = logging.getLogger(__name__)

# Cache local de passagens bíblicas extremamente populares para velocidade e robustez offline
POPULAR_SCRIPTURES = {
    "JHN.3.16": "Porque Deus tanto amou o mundo que deu o seu Filho Unigênito, para que todo o que nele crer não pereça, mas tenha a vida eterna.",
    "PSA.23.1": "O Senhor é o meu pastor; de nada terei falta.",
    "PHP.4.13": "Tudo posso naquele que me fortalece.",
    "ROM.8.28": "Sabemos que Deus age em todas as coisas para o bem daqueles que o amam, dos que foram chamados de acordo com o seu propósito.",
    "GEN.1.1": "No princípio Deus criou os céus e a terra.",
    "MAT.6.33": "Busquem, pois, em primeiro lugar o Reino de Deus e a sua justiça, e todas essas coisas lhes serão acrescentadas.",
}

class BibleService:
    @staticmethod
    def _display_reference(reference: str) -> str:
        return reference.title()

    @staticmethod
    def _validate_and_truncate_field(text: str, max_length: int, fallback_text: str) -> str:
        if not text:
            return fallback_text
            
        length = len(text)
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
    def _fetch_from_api(cls, reference_display: str) -> str:
        """
        Consulta a API pública e aberta bible-api.com de forma ultra-resiliente
        Retorna o array de versículos serializado em JSON.
        """
        ref_encoded = reference_display.strip().replace(" ", "+")
        url = f"https://bible-api.com/{ref_encoded}?translation=almeida"
        try:
            response = httpx.get(url, timeout=3.5)
            if response.status_code == 200:
                data = response.json()
                verses = data.get("verses", [])
                formatted_verses = [{"number": v.get("verse"), "text": v.get("text", "").strip()} for v in verses]
                return json.dumps(formatted_verses)
        except Exception as e:
            logger.warning("Falha ao consultar api externa bible-api.com: %s", e)
        return ""

    @classmethod
    def explain(cls, reference: str, user) -> Dict[str, Any]:
        # 1. Normalização Canônica (a nível de CAPÍTULO)
        can_id, book, chap, verses_req = NormalizationService.normalize(reference)
        ref_display = f"{book} {chap}" if chap else book
        
        # O display para o usuário continua sendo a referência completa que ele pediu
        full_reference_display = cls._display_reference(reference)
        
        book_id = can_id.split(".")[0]
        max_chap = NormalizationService.CHAPTER_COUNTS.get(book_id, 150)
        
        prev_chapter = f"{book} {chap - 1}" if chap > 1 else None
        next_chapter = f"{book} {chap + 1}" if chap > 0 and chap < max_chap else None

        # 2. Verificar se a Palavra já existe
        bible_passage = BiblePassage.objects.filter(canonical_id=can_id).first()
        
        # 3. Se a Palavra existe, verificar se existe explicação
        if bible_passage:
            explanation = PassageExplanation.objects.filter(passage=bible_passage).first()
            if explanation:
                log_event("cache_hit", content_type="bible_explanation", reference=can_id, content_id=explanation.id)
                log_event("bible_explanation_served_from_cache", reference=can_id, content_id=explanation.id, cached=True)
                with transaction.atomic():
                    GeneratedResponse.objects.create(
                        response_type='BIBLE',
                        user=user,
                        content_ref_id=explanation.id,
                        filter_status='clean',
                        metadata={"cached": True, "source": "foundation"}
                    )
                return {
                    "canonical_id": can_id,
                    "reference_display": full_reference_display,
                    "book_name": book,
                    "chapter": chap,
                    "verse_requested": verses_req,
                    "scripture_text": bible_passage.text_original,
                    "prev_chapter": prev_chapter,
                    "next_chapter": next_chapter,
                    "simple_explanation": explanation.simple_explanation,
                    "biblical_context": explanation.biblical_context,
                    "practical_application": explanation.practical_application,
                    "spiritual_reflection": explanation.spiritual_reflection,
                    "optional_prayer": explanation.optional_prayer,
                    "ai_generated": explanation.ai_generated,
                    "cached": True
                }

        log_event("cache_miss", content_type="bible_explanation", reference=can_id)

        # 4. Filtro de Entrada
        filter_res = ContentFilter.check_input(can_id)
        if filter_res.action == FilterAction.HARD_BLOCK:
            raise ContentBlockedException(category=filter_res.category)

        # 5. Scripture First: Garantir scripture_text puramente canônico de fonte confiável
        scripture_text = POPULAR_SCRIPTURES.get(can_id.upper())
        if not scripture_text:
            scripture_text = cls._fetch_from_api(ref_display)
            if not scripture_text:
                scripture_text = json.dumps([{"number": 1, "text": "A Palavra de Deus está sendo acolhida em silêncio e oração neste instante..."}])
                
        # Preparar texto contínuo para a IA ler facilmente
        ai_scripture_input = scripture_text
        try:
            parsed_verses = json.loads(scripture_text)
            ai_scripture_input = " ".join([f"[{v.get('number')}] {v.get('text')}" for v in parsed_verses])
        except:
            pass

        if verses_req:
            ai_scripture_input += f"\n\n[INSTRUÇÃO IMPORTANTE: O usuário focou a leitura especificamente no(s) versículo(s): {verses_req}. Embora você tenha o capítulo inteiro acima para contexto, direcione o 'Coração', o 'Contexto', a 'Reflexão' e a 'Oração' com um peso maior para iluminar a mensagem desta passagem em particular.]"

        # 6. Chamada de IA (I/O pesado fora de transações ativas do banco)
        ai_service = get_ai_service()
        input_hash = hashlib.sha256(can_id.encode()).hexdigest()
        
        ai_request = AIRequest.objects.create(
            request_type='bible',
            input_hash=input_hash,
            input_data={"canonical_id": can_id, "reference_display": ref_display},
            flagged_for_review=(filter_res.action == FilterAction.SOFT_FLAG),
            status='pending'
        )
        log_event("ai_request_started", request_type="bible", reference=can_id, ai_request_id=ai_request.id)

        try:
            # IA recebe o texto bíblico canônico predefinido!
            ai_response = ai_service.explain_passage(can_id, ref_display, ai_scripture_input, ai_request_id=ai_request.id)
        except Exception as e:
            logger.error("Falha ao chamar a API de IA no fluxo de explicação bíblica: %s", e)
            capture_exception(e, event="ai_request_failed", request_type="bible", reference=can_id, ai_request_id=ai_request.id)
            log_event("ai_request_failed", request_type="bible", reference=can_id, ai_request_id=ai_request.id, error_type=type(e).__name__)
            ai_request.status = 'failed'
            ai_request.output_data = {"error": str(e)}
            ai_request.save()
            raise e

        fallback = cls._get_fallback_response(full_reference_display)
        
        # 7. Validação e Truncamento
        simple_explanation = cls._validate_and_truncate_field(ai_response.get("simple_explanation", ""), 900, fallback["simple_explanation"])
        biblical_context = cls._validate_and_truncate_field(ai_response.get("biblical_context", ""), 600, fallback["biblical_context"])
        practical_application = cls._validate_and_truncate_field(ai_response.get("practical_application", ""), 600, fallback["practical_application"])
        spiritual_reflection = cls._validate_and_truncate_field(ai_response.get("spiritual_reflection", ""), 500, fallback["spiritual_reflection"])
        optional_prayer = cls._validate_and_truncate_field(ai_response.get("optional_prayer", ""), 400, fallback["optional_prayer"])

        # 8. Filtro de Saída
        ai_text_combined = f"{simple_explanation} {biblical_context} {practical_application} {spiritual_reflection} {optional_prayer}"
        out_filter_res = ContentFilter.check_output(ai_text_combined)
        
        if out_filter_res.action == FilterAction.HARD_BLOCK:
            ai_request.status = 'blocked'
            ai_request.save()
            raise ContentBlockedException(category=out_filter_res.category)
            
        ai_request.status = 'success'
        ai_request.output_data = ai_response
        
        # Copiar telemetria para o objeto local do Django para evitar sobrescrever campos do BD com NULL
        metrics = ai_response.get('_ai_metrics', {})
        if metrics:
            from decimal import Decimal
            ai_request.input_tokens = metrics.get('input_tokens')
            ai_request.output_tokens = metrics.get('output_tokens')
            ai_request.estimated_cost_usd = Decimal(str(round(metrics.get('estimated_cost_usd', 0.0), 10)))
            ai_request.duration_ms = metrics.get('duration_ms')
            ai_request.model_name = metrics.get('model_name')
            ai_request.endpoint_origin = metrics.get('endpoint_origin')
            ai_request.cache_hit = metrics.get('cache_hit', False)
            
        ai_request.save()
        log_event(
            "ai_request_success",
            request_type="bible",
            reference=can_id,
            ai_request_id=ai_request.id,
            duration_ms=ai_request.duration_ms,
            cache_hit=ai_request.cache_hit,
        )

        # Operações de escrita em banco agrupadas em bloco atômico curto
        with transaction.atomic():
            if not bible_passage:
                bible_passage = BiblePassage.objects.create(
                    canonical_id=can_id,
                    book_name=book,
                    chapter=chap,
                    verses=None,
                    text_original=scripture_text,
                    translation="almeida",
                    language="pt"
                )

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

            GeneratedResponse.objects.create(
                response_type='BIBLE',
                user=user,
                ai_request=ai_request,
                content_ref_id=explanation.id,
                filter_status='clean'
            )

        return {
            "canonical_id": can_id,
            "reference_display": full_reference_display,
            "book_name": book,
            "chapter": chap,
            "verse_requested": verses_req,
            "scripture_text": bible_passage.text_original,
            "prev_chapter": prev_chapter,
            "next_chapter": next_chapter,
            "simple_explanation": explanation.simple_explanation,
            "biblical_context": explanation.biblical_context,
            "practical_application": explanation.practical_application,
            "spiritual_reflection": explanation.spiritual_reflection,
            "optional_prayer": explanation.optional_prayer,
            "ai_generated": explanation.ai_generated,
            "cached": False
        }
