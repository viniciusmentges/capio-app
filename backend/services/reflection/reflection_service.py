import hashlib
import random
from typing import Dict, Any, Optional
from datetime import date as date_type, timedelta
from difflib import SequenceMatcher
from django.db import transaction
from django.utils import timezone
from apps.reflection.models import DailyReflection, UserReflectionResponse
from apps.ai_core.models import AIRequest, GeneratedResponse
from services.ai import get_ai_service
from services.exceptions import NotFoundException
from services.bible.normalization import NormalizationService
from apps.bible.models import BiblePassage
from services.observability import capture_exception, log_event

import logging

logger = logging.getLogger(__name__)

DAILY_REFLECTION_THEMES = [
    {
        "key": "contemplacao",
        "label": "Contemplação e Presença",
        "description": "Silêncio, repouso, escuta interior e Deus como centro.",
        "scripture_hints": ["Salmo 131", "Salmo 46:10", "Mateus 11:28-30"],
    },
    {
        "key": "coragem",
        "label": "Coragem e Firmeza",
        "description": "Enfrentar o que intimida, agir apesar do medo e confiar de forma ativa.",
        "scripture_hints": ["Josué 1:9", "1 Coríntios 16:13", "Isaías 40:31"],
    },
    {
        "key": "identidade",
        "label": "Identidade e Pertencimento",
        "description": "Quem somos diante de Deus, valor não baseado em desempenho e filiação espiritual.",
        "scripture_hints": ["Gálatas 2:20", "João 1:12", "1 João 3:1"],
    },
    {
        "key": "obediencia",
        "label": "Obediência e Fidelidade",
        "description": "Seguir a Deus quando é difícil, fé que age e fidelidade no cotidiano.",
        "scripture_hints": ["Lucas 9:23", "Tiago 2:17", "Deuteronômio 30:19-20"],
    },
    {
        "key": "perdao",
        "label": "Perdão e Reconciliação",
        "description": "Ser perdoado, perdoar o outro e restaurar pontes feridas.",
        "scripture_hints": ["Mateus 6:14-15", "Colossenses 3:13", "Lucas 15:20"],
    },
    {
        "key": "vocacao",
        "label": "Vocação e Trabalho",
        "description": "Chamado, trabalho, responsabilidade, excelência e presença de Deus na vida comum.",
        "scripture_hints": ["Colossenses 3:23", "Jeremias 29:7", "Gênesis 2:15"],
    },
    {
        "key": "esperanca",
        "label": "Esperança e Futuro",
        "description": "Promessas de Deus como âncora, futuro aberto e fé no que ainda não se vê.",
        "scripture_hints": ["Romanos 8:18-25", "Hebreus 11:1", "Lamentações 3:21-23"],
    },
    {
        "key": "graca",
        "label": "Graça e Misericórdia",
        "description": "Ser recebido sem merecer, misericórdia nova e amor que antecede o desempenho.",
        "scripture_hints": ["Efésios 2:8-9", "Lamentações 3:22-23", "Tito 3:5"],
    },
    {
        "key": "transformacao",
        "label": "Transformação e Maturidade",
        "description": "Mudança interior, crescimento lento, caráter formado e processo espiritual.",
        "scripture_hints": ["Romanos 5:3-5", "2 Coríntios 3:18", "Filipenses 1:6"],
    },
    {
        "key": "comunidade",
        "label": "Comunidade e Serviço",
        "description": "Pertencer ao corpo, servir sem reconhecimento e carregar o outro em amor.",
        "scripture_hints": ["Hebreus 10:24-25", "1 Coríntios 12:27", "Mateus 20:26-28"],
    },
    {
        "key": "tentacao",
        "label": "Tentação e Resistência",
        "description": "Luta interior, fidelidade custosa, resistência ao que atrai e dependência de Deus.",
        "scripture_hints": ["1 Coríntios 10:13", "Tiago 4:7", "Hebreus 4:15"],
    },
    {
        "key": "alegria",
        "label": "Alegria e Gratidão",
        "description": "Gratidão como postura, alegria não circunstancial e reconhecimento da bondade de Deus.",
        "scripture_hints": ["Filipenses 4:4-7", "Salmo 100", "1 Tessalonicenses 5:16-18"],
    },
    {
        "key": "sofrimento",
        "label": "Sofrimento e Redenção",
        "description": "Dor com sentido, cruz como caminho, consolo real e Deus presente no difícil.",
        "scripture_hints": ["2 Coríntios 4:17", "Romanos 8:28", "João 16:33"],
    },
    {
        "key": "tensao_espiritual",
        "label": "Tensão Espiritual",
        "description": "Vontade dividida, fé misturada com resistência, obediência relutante e conflito interior.",
        "scripture_hints": ["Marcos 9:24", "Romanos 7:19", "Mateus 26:39"],
    },
]

def _get_theme_for_date(target_date: date_type) -> dict:
    """
    Rotação temática determinística com entropia controlada.
    
    Objetivos:
    - mesma data gera sempre o mesmo tema;
    - todos os temas podem aparecer;
    - evitar padrões lineares previsíveis;
    - manter diversidade editorial.
    """
    day_of_year = target_date.timetuple().tm_yday
    seed_value = int(f"{target_date.year}{target_date.month:02d}{target_date.day:02d}")
    rng = random.Random(seed_value)
    
    # 5 é coprimo de 14, garantindo cobertura total periódica
    base_index = (day_of_year * 5 + target_date.year) % len(DAILY_REFLECTION_THEMES)
    offset = rng.randint(0, 2)
    
    theme_index = (base_index + offset) % len(DAILY_REFLECTION_THEMES)
    return DAILY_REFLECTION_THEMES[theme_index]

def _get_semantic_cooldown(target_date: date_type, days_back: int = 7) -> list:
    start_date = target_date - timedelta(days=days_back)
    end_date = target_date - timedelta(days=1)

    recent_themes = DailyReflection.objects.filter(
        date__range=(start_date, end_date)
    ).exclude(
        emotional_theme=""
    ).values_list("emotional_theme", flat=True)

    return list(dict.fromkeys(recent_themes))

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
            log_event("cache_miss", content_type="reflection", date=today)
            logger.info(f"Reflexão para {today} não encontrada. Iniciando geração sob demanda (Fallback).")
            cached = False
            reflection = cls.warmup_reflection(today)
        else:
            log_event("cache_hit", content_type="reflection", date=today, content_id=reflection.id)

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

        if cached:
            log_event("reflection_served_from_cache", content_id=reflection.id, date=today)

        return {
            "reflection": {
                "id": reflection.id,
                "public_id": str(reflection.public_id) if reflection.public_id else None,
                "date": reflection.date,
                "title": reflection.title,
                "scripture_reference": reflection.scripture_reference,
                "scripture_text": reflection.scripture_text,
                "reflection_body": reflection.reflection_body,
                "guiding_question": reflection.guiding_question,
                "closing_prayer": reflection.closing_prayer,
                "share_quote": reflection.share_quote,
                "share_text": reflection.share_text,
                "share_bg_image": reflection.share_bg_image,
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

        # Calcular o tema determinístico e obter resfriamento semântico
        theme = _get_theme_for_date(target_date)
        semantic_cooldown = _get_semantic_cooldown(target_date)

        ai_service = get_ai_service()
        date_str = target_date.isoformat()
        input_hash = hashlib.sha256(f"reflection-{date_str}".encode()).hexdigest()

        ai_request = AIRequest.objects.create(
            request_type='reflection',
            input_hash=input_hash,
            input_data={
                "date": date_str,
                "blacklist": blacklist,
                "theme": theme,
                "semantic_cooldown": semantic_cooldown
            },
            status='pending'
        )
        log_event("ai_request_started", request_type="reflection", ai_request_id=ai_request.id)

        try:
            # Passamos a blacklist, o tema e o cooldown para o serviço de AI
            ai_response = ai_service.generate_reflection(
                date=date_str,
                theme=theme,
                excluded_passages=blacklist,
                semantic_cooldown=semantic_cooldown,
                ai_request_id=ai_request.id
            )
            
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

            # Extrair chaves
            reflection_body = ai_response.get("reflection_body", "")
            share_quote = ai_response.get("share_quote", "")
            title = ai_response.get("title", "")
            closing_prayer = ai_response.get("closing_prayer", "")
            
            night_word = ai_response.get("night_word", "")
            night_prayer = ai_response.get("night_prayer", "")

            # --- PROTEÇÃO ANTI-REPETIÇÃO AVANÇADA ---
            # Se night_word for parecida com algo já dito, aplicar fallback
            clean_night_word = night_word.strip().lower()
            clean_share_quote = share_quote.strip().lower()
            clean_reflection = reflection_body.strip().lower()
            clean_title = title.strip().lower()
            
            def get_similarity(a: str, b: str) -> float:
                if not a or not b: return 0.0
                return SequenceMatcher(None, a, b).ratio()
            
            similarity_with_quote = get_similarity(clean_night_word, clean_share_quote)
            
            # Para o corpo da reflexão, o SequenceMatcher.ratio() pode ser baixo porque o corpo é muito longo,
            # mas vamos checar substring matching mais robusto ou a similaridade caso seja muito alta.
            # Um método melhor para textos longos é checar se a frase está contida, ou focar em blocos.
            # Por segurança, mantemos o `in` e a similaridade.
            similarity_with_body = get_similarity(clean_night_word, clean_reflection)
            
            is_empty = clean_night_word == ""
            is_literal = (clean_night_word in clean_reflection) or (clean_night_word in clean_share_quote) or (clean_night_word in clean_title)
            is_similar_quote = similarity_with_quote >= 0.45
            is_similar_body = similarity_with_body >= 0.55
            
            if is_empty or is_literal or is_similar_quote or is_similar_body:
                reason = "repetition_or_empty"
                if is_similar_quote: reason = "similarity_quote_45"
                elif is_similar_body: reason = "similarity_body_55"
                
                log_event("night_word_fallback_used", reason=reason, date=target_date)
                logger.warning(f"[CAPIO] Fallback noturno acionado para {target_date}: {night_word} (Motivo: {reason})")
                
                # Fallback seguro e neutro, que não repete o corpo
                night_word = "Há um repouso silencioso que nos aguarda no fim de tudo."
                
            clean_night_prayer = night_prayer.strip().lower()
            clean_closing_prayer = closing_prayer.strip().lower()
            similarity_prayer = get_similarity(clean_night_prayer, clean_closing_prayer)
            
            if similarity_prayer >= 0.50 or clean_night_prayer == "":
                reason = "similarity_prayer_50" if similarity_prayer >= 0.50 else "empty"
                log_event("night_prayer_fallback_used", reason=reason, date=target_date)
                night_prayer = "Senhor, entrego este dia em tuas mãos. Que a noite traga repouso e a certeza de que não estou só. Amém."

            reflection = DailyReflection.objects.create(
                date=target_date,
                passage=bible_passage,
                title=title,
                scripture_reference=ref_raw,
                scripture_text=bible_passage.text_original,
                reflection_body=reflection_body,
                guiding_question=ai_response.get("guiding_question", ""),
                closing_prayer=closing_prayer,
                share_quote=share_quote,
                night_word=night_word,
                night_prayer=night_prayer,
                ai_generated=ai_response.get("ai_generated", True),
                emotional_theme=ai_response.get("emotional_theme", ""),
                theme_key=theme.get("key", "")
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
            log_event(
                "ai_request_success",
                request_type="reflection",
                ai_request_id=ai_request.id,
                duration_ms=ai_request.duration_ms,
                cache_hit=ai_request.cache_hit,
            )
            return reflection

        except Exception as e:
            ai_request.status = 'error'
            ai_request.metadata = {"error": str(e)}
            ai_request.save()
            logger.error(f"Falha crítica no ritual de reflexão: {str(e)}")
            capture_exception(e, event="ai_request_failed", request_type="reflection", ai_request_id=ai_request.id)
            log_event("ai_request_failed", request_type="reflection", ai_request_id=ai_request.id, error_type=type(e).__name__)
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
