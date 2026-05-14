import json
import os
from django.conf import settings
from typing import Dict, Any
from .base import AIService

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

    def explain_passage(self, reference_normalized: str, reference_display: str) -> Dict[str, Any]:
        filepath = os.path.join(self.fixtures_dir, 'bible', 'default.json')
        data = self._load_json(filepath)
        if data:
            return data
            
        return {
            "biblical_context": f"A passagem de {reference_display} nos situa no encontro entre a Palavra e o silêncio.",
            "scripture_text": "Texto bíblico indisponível no mock.",
            "simple_explanation": "O coração desta mensagem fala sobre a presença constante de Deus.",
            "spiritual_reflection": "Há um mistério escondido na simplicidade destes versículos que convida ao repouso.",
            "practical_application": "O eco desta Palavra hoje convida a um gesto de paciência e escuta.",
            "optional_prayer": "Senhor, dai-me um coração atento à Vossa voz.",
            "ai_generated": False
        }


    def devotional_for_emotion(self, emotion_name: str) -> Dict[str, Any]:
        slug = emotion_name.lower().replace(" ", "-").replace("ç", "c").replace("ã", "a")
        filepath = os.path.join(self.fixtures_dir, 'devotional', f'{slug}.json')
        
        data = self._load_json(filepath)
        if data:
            return data
            
        # Fallback if specific emotion fixture missing
        filepath_default = os.path.join(self.fixtures_dir, 'devotional', 'ansioso.json')
        data_default = self._load_json(filepath_default)
        if data_default:
            return data_default
            
        return {
            "title": f"O repouso na {emotion_name}",
            "scripture_reference": "Salmos 23:1",
            "scripture_text": "O Senhor é meu pastor, nada me faltará.",
            "reflection": "No silêncio do pastor, a alma encontra o que não pode ser comprado.",
            "practical_application": "Respire fundo e entregue o peso do agora.",
            "guiding_question": "Onde o silêncio de Deus mais te toca neste momento?",
            "prayer": "Senhor, eu confio.",
            "ai_generated": False
        }

    def generate_reflection(self, date: str) -> Dict[str, Any]:
        filepath = os.path.join(self.fixtures_dir, 'reflection', 'default.json')
        data = self._load_json(filepath)
        if data:
            return data
            
        return {
            "title": "O amanhecer do Verbo",
            "scripture_reference": "João 1:1",
            "scripture_text": "No princípio era o Verbo.",
            "reflection_body": "O dia começa com a Palavra que cria e sustenta a vida.",
            "guiding_question": "Como o Verbo quer habitar em seu silêncio hoje?",
            "closing_prayer": "Fica conosco, Senhor.",
            "ai_generated": False
        }

