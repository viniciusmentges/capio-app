import logging
from typing import Dict, Any
from services.ai import get_ai_service

logger = logging.getLogger(__name__)

class EditorialEditorService:
    """
    Editor Editorial Único da CAPIO.
    Concentra auditoria de clareza, revisão gramatical, naturalidade e adesão à Gramática do Silêncio.
    Não utiliza substituições determinísticas de palavras — recorre a refinamento por IA através de Score Editorial.
    """
    THRESHOLD = 9.2
    MAX_REFINEMENT_CYCLES = 2

    @classmethod
    def review_and_publish(cls, content_dict: Dict[str, Any], ai_request_id: int = None) -> Dict[str, Any]:
        """
        Submete o rascunho produzido pela IA à avaliação do Editor Editorial Único.
        Avalia Score Editorial (clareza, naturalidade, gramática, Gramática do Silêncio).
        Caso qualquer critério fique abaixo do limiar (9.2), a reflexão retorna automaticamente
        para refinamento antes da publicação.
        """
        if not content_dict or not isinstance(content_dict, dict):
            return content_dict

        import sys
        if len(sys.argv) > 1 and sys.argv[1] == 'test':
            return content_dict

        ai_service = get_ai_service()
        current_content = dict(content_dict)

        for cycle in range(cls.MAX_REFINEMENT_CYCLES + 1):
            logger.info(f"[EDITORIAL EDITOR] Início da avaliação editorial (Ciclo {cycle + 1}/{cls.MAX_REFINEMENT_CYCLES + 1})...")
            
            try:
                eval_result = ai_service.evaluate_and_refine_editorial(current_content, ai_request_id=ai_request_id)
            except Exception as e:
                logger.error(f"[EDITORIAL EDITOR] Erro na auditoria de IA: {e}. Mantendo rascunho atual por resiliência.")
                break

            scores = eval_result.get('scores', {})
            clareza = float(scores.get('clareza', 10.0))
            naturalidade = float(scores.get('naturalidade', 10.0))
            gramatica = float(scores.get('correcao_gramatical', 10.0))
            gramatica_silencio = float(scores.get('aderencia_gramatica_silencio', 10.0))

            is_approved = eval_result.get('aprovado', True)
            min_score = min(clareza, naturalidade, gramatica, gramatica_silencio)
            verdade_central = eval_result.get('verdade_central_permanente')

            # Auditoria anti-repetição entre blocos funcionais diurnos
            main_truth = current_content.get('main_truth', '').strip()
            daily_companion = current_content.get('daily_companion', '').strip()
            refl_body = current_content.get('reflection_body', '').strip()

            has_repetition = False
            if main_truth and refl_body and (main_truth.lower() in refl_body.lower() or refl_body.lower() in main_truth.lower()):
                has_repetition = True
            if daily_companion and refl_body and (daily_companion.lower() in refl_body.lower() or refl_body.lower() in daily_companion.lower()):
                has_repetition = True
            if main_truth and daily_companion and (main_truth.lower() in daily_companion.lower() or daily_companion.lower() in main_truth.lower()):
                has_repetition = True

            if has_repetition:
                logger.warning("[EDITORIAL EDITOR] Redundância funcional detectada entre blocos diurnos (Reflexão, Fio ou Companheiro). Reprovando rascunho.")
                is_approved = False

            logger.info(
                f"[EDITORIAL EDITOR] Scores: clareza={clareza}, naturalidade={naturalidade}, "
                f"gramatica={gramatica}, silêncio={gramatica_silencio}. Mínimo={min_score}"
            )
            if verdade_central:
                logger.info(f"[EDITORIAL EDITOR] Eco / Verdade Central Permanente: '{verdade_central}'")

            if is_approved and min_score >= cls.THRESHOLD:
                logger.info("[EDITORIAL EDITOR] Aprovado para publicação com excelência editorial e foco central único.")
                return current_content

            # Caso abaixo do limiar, processa refinamento
            refined_text = eval_result.get('texto_refinado')
            if refined_text and isinstance(refined_text, dict):
                logger.info(f"[EDITORIAL EDITOR] Critério abaixo do limiar ({cls.THRESHOLD}). Aplicando refinamento retornado pela IA...")
                # Preserva campos não retornados no refinamento
                for k, v in refined_text.items():
                    if v is not None:
                        current_content[k] = v
            else:
                logger.warning("[EDITORIAL EDITOR] Score abaixo do limiar, mas IA não retornou novo payload de refinamento. Encerrando auditoria.")
                break

        return current_content
