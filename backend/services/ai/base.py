from abc import ABC, abstractmethod
from typing import Dict, Any

class AIService(ABC):
    @abstractmethod
    def explain_passage(self, reference_normalized: str, reference_display: str, scripture_text: str) -> Dict[str, Any]:
        """Returns: {'biblical_context': str, 'simple_explanation': str, 'spiritual_reflection': str, 'practical_application': str, 'optional_prayer': str, 'ai_generated': bool}"""
        pass

    @abstractmethod
    def generate_reading_focus(self, chapter_text: str, reference_display: str, verse_start: int, verse_end: int) -> Dict[str, Any]:
        """Returns: {'title': str, 'content': str}"""
        pass

    @abstractmethod
    def devotional_for_emotion(self, emotion_name: str, reference_display: str, scripture_text: str) -> Dict[str, Any]:
        """Returns: {'title': str, 'reflection': str, 'practical_application': str, 'guiding_question': str, 'prayer': str, 'ai_generated': bool}"""
        pass

    @abstractmethod
    def generate_reflection(self, date: str, theme: dict = None, excluded_passages: list = None, semantic_cooldown: list = None, ai_request_id: int = None) -> Dict[str, Any]:
        """Returns: {'title': str, 'scripture_reference': str, 'scripture_text': str, 'reflection_body': str, 'guiding_question': str, 'closing_prayer': str, 'ai_generated': bool}"""
        pass

    @abstractmethod
    def editorial_generate_devotional(self, emotion_name: str, tone_or_direction: str = None) -> Dict[str, Any]:
        """Returns: {'title': str, 'scripture_reference': str, 'scripture_text': str, 'reflection': str, 'prayer': str, 'share_quote': str, 'emotional_theme': str, 'ai_generated': bool}"""
        pass

    @abstractmethod
    def generate_share_quote(self, reflection: str) -> str:
        """Gera um share_quote (fragmento contemplativo) com base em uma meditação/reflexão textual."""
        pass

    @abstractmethod
    def evaluate_and_refine_editorial(self, content_dict: Dict[str, Any], ai_request_id: int = None) -> Dict[str, Any]:
        """Avalia o conteúdo gerado atribuindo um Score Editorial (0 a 10) e reescreve com prompt de refinamento se abaixo do limiar."""
        pass

