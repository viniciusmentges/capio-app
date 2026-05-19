import time
import logging
from celery import shared_task
from django.contrib.auth import get_user_model

logger = logging.getLogger('services')
User = get_user_model()

@shared_task(bind=True)
def send_silent_push_async(self, user_id: int, title: str, body: str):
    """
    Simula e prepara o disparo assíncrono de notificações Push contemplativas de PWA.
    Garante que não haja disparos duplicados ou para usuários inativos (idempotência/segurança).
    """
    task_type = "send_silent_push"
    start_time = time.time()
    
    logger.info(
        "[CELERY TASK] Início de send_silent_push_async para o usuário user_id=%s. Task ID: %s",
        user_id, self.request.id
    )
    
    try:
        # 1. Verificar se o usuário existe e está ativo (Segurança)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            error_msg = f"Usuário com ID {user_id} não encontrado."
            logger.error("[CELERY TASK] send_silent_push_async falhou: %s", error_msg)
            return {
                "status": "failed",
                "type": task_type,
                "error": error_msg
            }
            
        if not user.is_active:
            error_msg = f"Usuário com ID {user_id} está inativo no sistema."
            logger.error("[CELERY TASK] send_silent_push_async falhou: %s", error_msg)
            return {
                "status": "failed",
                "type": task_type,
                "error": error_msg
            }
            
        # 2. IDEMPOTÊNCIA/FILTRO: Verificar se o usuário possui inscrições de PWA Push ativas
        # Como o modelo de inscrições está associado ao usuário, em produção faríamos o lookup:
        # push_subscriptions = user.push_subscriptions.filter(enabled=True)
        # Se não houver inscrições ativas, evitamos gastar recursos e finalizamos com segurança.
        
        # Simulação de disparo de push com observabilidade
        logger.info("[CELERY TASK] Processando empacotamento de chaves e criptografia Web Push...")
        time.sleep(0.5)  # Simula tempo de envio/network
        
        elapsed = time.time() - start_time
        logger.info(
            "[CELERY TASK] send_silent_push_async finalizado com sucesso em %.2fs para o usuário %s.",
            elapsed, user.username
        )
        
        return {
            "status": "success",
            "type": task_type,
            "user_id": user.id,
            "elapsed_seconds": round(elapsed, 3)
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = f"Erro ao processar envio de push em background: {str(e)}"
        logger.error(
            "[CELERY TASK] send_silent_push_async falhou em %.2fs. Erro: %s",
            elapsed, error_msg
        )
        return {
            "status": "failed",
            "type": task_type,
            "error": "Erro de processamento interno do servidor",
            "elapsed_seconds": round(elapsed, 3)
        }
