import time
import logging
from zoneinfo import ZoneInfo
from datetime import timedelta
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger('services')
User = get_user_model()

def should_send_push(user, subscription) -> bool:
    """
    Retorna True se a notificação deve ser enviada para a inscrição específica,
    respeitando a Gramática do Silêncio e a calibração de presença da CAPIO.
    """
    from apps.reflection.models import DailyReflection
    from apps.ai_core.models import GeneratedResponse

    # 1. Respeitar ausência: se o usuário não acessou nos últimos 5 dias, desacelerar
    five_days_ago = timezone.now() - timedelta(days=5)
    recent_access = GeneratedResponse.objects.filter(
        user=user,
        created_at__gte=five_days_ago
    ).exists()
    
    if not recent_access:
        logger.info(
            "[RITUAL SILENCE] Respeitando ausência do usuário %s. Sem acessos nos últimos 5 dias. Push silenciado.",
            user.username
        )
        return False

    # 2. Silenciamento inteligente noturno:
    # Se a preferência da inscrição é noturna ('evening') e o usuário já leu a reflexão de hoje, silenciar.
    if subscription.preferred_time == 'evening':
        today = timezone.localtime().date()
        reflection = DailyReflection.objects.filter(date=today).first()
        if reflection:
            has_read_today = GeneratedResponse.objects.filter(
                response_type='REFLECTION',
                user=user,
                content_ref_id=reflection.id
            ).exists()
            if has_read_today:
                logger.info(
                    "[RITUAL SILENCE] Supressão ativa para %s. Reflexão de hoje já lida. Push noturno cancelado.",
                    user.username
                )
                return False

    # 3. Janelas ritualísticas de fuso horário local:
    # Manhã: 6h–9h | Noite: 19h–22h | Qualquer momento: sem restrição de janela
    try:
        tz = ZoneInfo(subscription.timezone)
        user_local_now = timezone.localtime(timezone.now(), tz)
        local_hour = user_local_now.hour
    except Exception:
        local_hour = timezone.localtime().hour # Fallback seguro

    if subscription.preferred_time == 'morning' and not (6 <= local_hour <= 9):
        logger.warning(
            "[RITUAL SILENCE] Push fora da janela matutina local (6h-9h) para %s. Hora atual local: %s. Envio cancelado.",
            user.username, local_hour
        )
        return False
    elif subscription.preferred_time == 'evening' and not (19 <= local_hour <= 22):
        logger.warning(
            "[RITUAL SILENCE] Push fora da janela noturna local (19h-22h) para %s. Hora atual local: %s. Envio cancelado.",
            user.username, local_hour
        )
        return False

    return True

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
            
        # 2. IDEMPOTÊNCIA/FILTRO: Verificar se o usuário possui inscrições de PWA Push ativas e válidas
        subscriptions = user.push_subscriptions.filter(enabled=True)
        if not subscriptions.exists():
            logger.info("[CELERY TASK] Usuário %s não possui inscrições push ativas.", user.username)
            return {
                "status": "skipped",
                "type": task_type,
                "reason": "Sem inscrições push ativas."
            }

        # Filtrar inscrições de acordo com a Gramática do Silêncio
        valid_subscriptions = []
        for sub in subscriptions:
            if should_send_push(user, sub):
                valid_subscriptions.append(sub)

        if not valid_subscriptions:
            logger.info("[CELERY TASK] Todos os pushes foram silenciados para %s pela Gramática do Silêncio.", user.username)
            return {
                "status": "silenced",
                "type": task_type,
                "reason": "Silenciado pela Gramática do Silêncio."
            }
        
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
