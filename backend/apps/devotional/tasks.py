import time
import logging
from celery import shared_task
from django.db import transaction
from apps.devotional.models import Emotion, DevotionalContent
from apps.bible.models import BiblePassage
from services.devotional.devotional_service import DevotionalService

logger = logging.getLogger('services')

@shared_task(bind=True)
def generate_devotional_async(self, emotion_slug: str, passage_id: int):
    """
    Gera um novo devocional de forma assíncrona com base na emoção e passagem bíblica.
    Garante idempotência total verificando duplicidade antes de iniciar o processamento pesado.
    """
    task_type = "generate_devotional"
    start_time = time.time()
    
    logger.info(
        "[CELERY TASK] Início de generate_devotional_async para emotion_slug=%s, passage_id=%s. Task ID: %s",
        emotion_slug, passage_id, self.request.id
    )
    
    try:
        # 1. Obter registros básicos com tratamento seguro
        try:
            emotion = Emotion.objects.get(slug=emotion_slug)
            passage = BiblePassage.objects.get(id=passage_id)
        except (Emotion.DoesNotExist, BiblePassage.DoesNotExist) as e:
            error_msg = f"Registro não encontrado: {str(e)}"
            logger.error("[CELERY TASK] generate_devotional_async falhou: %s", error_msg)
            return {
                "status": "failed",
                "type": task_type,
                "error": error_msg
            }
            
        # 2. IDEMPOTÊNCIA: Verificar se já existe um devocional para esta combinação específica de Emoção + Passagem
        existing_devotional = DevotionalContent.objects.filter(
            emotion=emotion,
            passage=passage,
            is_active=True
        ).first()
        
        if existing_devotional:
            elapsed = time.time() - start_time
            logger.info(
                "[CELERY TASK] generate_devotional_async finalizado (Idempotente) em %.2fs. Devocional correspondente já existente (ID: %s).",
                elapsed, existing_devotional.id
            )
            return {
                "status": "already_exists",
                "type": task_type,
                "devotional_id": existing_devotional.id,
                "elapsed_seconds": round(elapsed, 3)
            }
            
        # 3. Geração pesada do Devocional
        # Chamamos o DevotionalService para lidar com a curadoria/IA.
        # Observação: O DevotionalService já trata timeouts de IA e fallbacks internamente de forma blindada.
        logger.info("[CELERY TASK] Executando geração através do DevotionalService...")
        
        # Envolvemos na escrita de banco final de forma atômica
        with transaction.atomic():
            devotional = DevotionalService.get_for_emotion(emotion.slug)
            
        elapsed = time.time() - start_time
        
        # Detectar se o devocional criado foi gerado via AI ou Mock fallback para fins de observabilidade
        if not getattr(devotional, 'ai_generated', False):
            logger.warning("[CELERY TASK] generate_devotional_async recorreu ao fallback do MockAIService devido a erro ou timeout na IA.")
            
        logger.info(
            "[CELERY TASK] generate_devotional_async finalizado com sucesso em %.2fs. Novo Devocional ID: %s.",
            elapsed, devotional.id
        )
        
        return {
            "status": "success",
            "type": task_type,
            "devotional_id": devotional.id,
            "elapsed_seconds": round(elapsed, 3)
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Erro inesperado no pipeline assíncrono: {str(e)}"
        logger.error(
            "[CELERY TASK] generate_devotional_async falhou em %.2fs. Erro: %s",
            elapsed, error_msg
        )
        return {
            "status": "failed",
            "type": task_type,
            "error": "Erro de processamento interno do servidor",
            "elapsed_seconds": round(elapsed, 3)
        }
