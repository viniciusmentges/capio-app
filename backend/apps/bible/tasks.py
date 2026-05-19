import time
import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from apps.bible.models import PassageExplanation
from services.bible.normalization import NormalizationService
from services.bible.explanation_service import BibleService

logger = logging.getLogger('services')
User = get_user_model()

@shared_task(bind=True)
def generate_bible_explanation_async(self, reference: str, user_id: int = None):
    """
    Gera uma explicação exegética para uma passagem bíblica de forma assíncrona.
    Garante idempotência normalizando a referência e verificando cache de banco antes da IA.
    """
    task_type = "generate_bible_explanation"
    start_time = time.time()
    
    logger.info(
        "[CELERY TASK] Início de generate_bible_explanation_async para reference='%s', user_id=%s. Task ID: %s",
        reference, user_id, self.request.id
    )
    
    try:
        # 1. Normalização Canônica da Referência
        try:
            can_id, _, _, _ = NormalizationService.normalize(reference)
        except Exception as e:
            error_msg = f"Falha ao normalizar referência: {str(e)}"
            logger.error("[CELERY TASK] generate_bible_explanation_async falhou: %s", error_msg)
            return {
                "status": "failed",
                "type": task_type,
                "error": error_msg
            }
            
        # 2. Resolução do Usuário (se fornecido)
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                logger.warning("[CELERY TASK] Usuário com ID %s não encontrado. Prosseguindo sem usuário associado.", user_id)
                
        # 3. IDEMPOTÊNCIA: Verificar se já existe explicação para a referência normalizada
        existing_explanation = PassageExplanation.objects.filter(
            reference_normalized=can_id
        ).first()
        
        if existing_explanation:
            elapsed = time.time() - start_time
            logger.info(
                "[CELERY TASK] generate_bible_explanation_async finalizado (Idempotente) em %.2fs. Explicação já existente (ID: %s).",
                elapsed, existing_explanation.id
            )
            return {
                "status": "already_exists",
                "type": task_type,
                "explanation_id": existing_explanation.id,
                "elapsed_seconds": round(elapsed, 3)
            }
            
        # 4. Geração pesada através do BibleService
        logger.info("[CELERY TASK] Executando geração através do BibleService...")
        result = BibleService.explain(reference, user)
        
        # Encontrar a explicação recém-gerada
        explanation = PassageExplanation.objects.filter(reference_normalized=can_id).first()
        explanation_id = explanation.id if explanation else None
        
        elapsed = time.time() - start_time
        
        # Detectar se recorreu a fallback (não gerada por IA) para fins de observabilidade
        if result and not result.get("ai_generated", True):
            logger.warning("[CELERY TASK] generate_bible_explanation_async recorreu ao fallback do MockAIService devido a erro ou timeout na IA.")
            
        logger.info(
            "[CELERY TASK] generate_bible_explanation_async finalizado com sucesso em %.2fs. Nova Explicação ID: %s.",
            elapsed, explanation_id
        )
        
        return {
            "status": "success",
            "type": task_type,
            "explanation_id": explanation_id,
            "elapsed_seconds": round(elapsed, 3)
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Erro inesperado no pipeline assíncrono: {str(e)}"
        logger.error(
            "[CELERY TASK] generate_bible_explanation_async falhou em %.2fs. Erro: %s",
            elapsed, error_msg
        )
        return {
            "status": "failed",
            "type": task_type,
            "error": "Erro de processamento interno do servidor",
            "elapsed_seconds": round(elapsed, 3)
        }
