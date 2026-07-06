import json
import os
import logging
from django.conf import settings
from typing import Dict, Any
from .base import AIService

logger = logging.getLogger('services')

class MockAIService(AIService):
    def __init__(self):
        # We assume BASE_DIR is the root of the Django project
        self.fixtures_dir = os.path.join(settings.BASE_DIR, 'fixtures', 'mock_responses')

    def _load_json(self, filepath: str) -> Dict[str, Any]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def explain_passage(self, reference_normalized: str, reference_display: str, scripture_text: str) -> Dict[str, Any]:
        logger.warning(f"[CAPIO AI] Fallback acionado no fluxo de explicação bíblica para a passagem {reference_display}. Servindo do MockAIService por falha de API ou ambiente.")
        
        filepath = os.path.join(self.fixtures_dir, 'bible', 'default.json')
        data = self._load_json(filepath)
        if data:
            data['scripture_text'] = scripture_text
            return data
            
        return {
            "biblical_context": f"A passagem de {reference_display} nos situa no encontro entre a Palavra e o silêncio.",
            "scripture_text": scripture_text,
            "simple_explanation": "O coração desta mensagem fala sobre a presença constante de Deus.",
            "spiritual_reflection": "Há um mistério escondido na simplicidade destes versículos que convida ao repouso.",
            "practical_application": "O eco desta Palavra hoje convida a um gesto de paciência e escuta.",
            "optional_prayer": "Senhor, dai-me um coração atento à Vossa voz.",
            "ai_generated": False
        }

    def generate_reading_focus(self, chapter_text: str, reference_display: str, verse_start: int, verse_end: int) -> Dict[str, Any]:
        logger.warning(f"[CAPIO AI] Mock acionado no fluxo de foco da leitura para {reference_display}.")
        return {
            "title": "O foco desta leitura",
            "content": f"A meditação no recorte dos versículos {verse_start} ao {verse_end} traz luz à importância da obediência silenciosa.",
            "ai_generated": False
        }

    def devotional_for_emotion(self, emotion_name: str, reference_display: str, scripture_text: str, *args, **kwargs) -> Dict[str, Any]:
        logger.warning(f"[CAPIO AI] Fallback acionado no fluxo de devocional por emoção para {emotion_name}. Servindo do MockAIService por falha de API ou ambiente.")
        
        slug = emotion_name.lower().replace(" ", "-").replace("ç", "c").replace("ã", "a")
        filepath = os.path.join(self.fixtures_dir, 'devotional', f'{slug}.json')
        
        data = self._load_json(filepath)
        if not data:
            filepath_default = os.path.join(self.fixtures_dir, 'devotional', 'ansioso.json')
            data = self._load_json(filepath_default)
            
        if data:
            data['scripture_reference'] = reference_display
            data['scripture_text'] = scripture_text
            if 'share_quote' not in data:
                data['share_quote'] = "No silêncio do pastor, a alma encontra o que não pode ser comprado."
            if 'main_truth' not in data:
                data['main_truth'] = "O cuidado de Deus antecede a preocupação e sustenta a alma em repouso."
            if 'daily_companion' not in data:
                data['daily_companion'] = "Quando a pressa tentar tomar o controle, lembre-se do cuidado silencioso que te sustenta."
            if 'emotional_theme' not in data:
                data['emotional_theme'] = f"Repouso na {emotion_name}"
            return data
            
        return {
            "title": f"O repouso na {emotion_name}",
            "scripture_reference": reference_display,
            "scripture_text": scripture_text,
            "reflection": "No silêncio do pastor, a alma encontra o que não pode ser comprado. Há um convite permanente para depositar o peso onde ele pode ser sustentado. Não é uma técnica de alívio, mas um ato de reconhecimento: o cuidado de Deus antecede a preocupação e a envolve com atenção real.",
            "practical_application": "Respire fundo e entregue o peso do agora.",
            "guiding_question": "Onde o silêncio de Deus mais te toca neste momento?",
            "prayer": "Senhor, eu confio.",
            "share_quote": "No silêncio do pastor, a alma encontra o que não pode ser comprado.",
            "main_truth": "O cuidado de Deus antecede a preocupação e sustenta a alma em repouso.",
            "daily_companion": "Quando a pressa tentar tomar o controle, lembre-se do cuidado silencioso que te sustenta.",
            "emotional_theme": f"Repouso na {emotion_name}",
            "ai_generated": False
        }

    def generate_reflection(self, date: str, theme: dict = None, excluded_passages: list = None, semantic_cooldown: list = None, ai_request_id: int = None) -> Dict[str, Any]:
        logger.warning(f"[CAPIO AI] Fallback acionado no fluxo de reflexão diária para a data {date}. Servindo do MockAIService por falha de API ou ambiente.")
        
        filepath = os.path.join(self.fixtures_dir, 'reflection', 'default.json')
        data = self._load_json(filepath)
        if data:
            data['emotional_theme'] = "tema simulado"
            return data
            
        return {
            "title": "O amanhecer do Verbo",
            "scripture_reference": "João 1:1",
            "scripture_text": "No princípio era o Verbo.",
            "central_truth": "Tudo começa em Deus antes das pressas humanas.",
            "reflection_body": "O dia começa com a Palavra que cria e sustenta a vida. Antes de qualquer ruído de nossas preocupações, o Verbo já está presente.",
            "main_truth": "A Palavra de Deus antecede a rotina e sustenta cada hora. Tudo começa nela.",
            "daily_companion": "Quando a pressa tentar tomar o controle nas próximas horas, a lembrança de que Deus sustenta este dia poderá voltar silenciosamente a você.",
            "guiding_question": "Como o Verbo quer habitar em seu silêncio hoje?",
            "closing_prayer": "Fica conosco, Senhor.",
            "share_quote": "A Palavra no princípio cria o silêncio que sustenta a nossa alma.",
            "emotional_theme": "tema simulado",
            "ai_generated": False
        }

    def editorial_generate_devotional(
        self,
        emotion_name: str,
        tone_or_direction: str = None,
        excluded_passages: list = None,
        excluded_themes: list = None,
        excluded_titles: list = None,
        semantic_cooldown_words: list = None,
    ) -> Dict[str, Any]:
        logger.warning(f"[CAPIO AI] Mock acionado no fluxo editorial de devocional para a emoção {emotion_name} e tom/direção {tone_or_direction}.")
        return {
            "title": f"O cuidado de Deus em {emotion_name}",
            "scripture_reference": "1 Pedro 5:7",
            "scripture_text": "Lancem sobre ele toda a sua ansiedade, porque ele tem cuidado de vocês.",
            "reflection": "Há um convite permanente para depositar o peso onde ele pode ser sustentado. Não é uma técnica de alívio, mas um ato de reconhecimento: o cuidado de Deus antecede a preocupação e a envolve com atenção real.",
            "prayer": "Senhor, recebo o teu cuidado como resposta ao meu peso. Não preciso carregar sozinho.",
            "share_quote": "O cuidado de Deus antecede a preocupação e a envolve com atenção real.",
            "main_truth": "O cuidado divino antecede o fardo humano e sustenta a alma em repouso.",
            "daily_companion": "Quando a pressa tentar tomar o controle, a presença silenciosa do Pastor caminha ao seu lado.",
            "emotional_theme": f"Cuidado de Deus na {emotion_name}" if not tone_or_direction else tone_or_direction,
            "ai_generated": False
        }

    def generate_share_quote(self, reflection: str) -> str:
        logger.warning("[CAPIO AI] Mock acionado no fluxo de geração de share_quote.")
        # Retorna um pedaço curto da meditação ou uma frase mock
        return "O silêncio é o solo fértil onde a oração de entrega amadurece."

    def evaluate_and_refine_editorial(self, content_dict: Dict[str, Any], ai_request_id: int = None) -> Dict[str, Any]:
        logger.warning("[CAPIO AI] Mock acionado no fluxo de evaluate_and_refine_editorial.")
        return {
            "scores": {
                "clareza": 10.0,
                "naturalidade": 10.0,
                "correcao_gramatical": 10.0,
                "aderencia_gramatica_silencio": 10.0
            },
            "aprovado": True,
            "verdade_central_permanente": "O cuidado de Deus antecede a preocupação e sustenta a nossa alma em silêncio.",
            "texto_refinado": None
        }

