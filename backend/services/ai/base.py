from abc import ABC, abstractmethod
from typing import Dict, Any

class AIService(ABC):
    @abstractmethod
    def explain_passage(self, reference_normalized: str, reference_display: str, scripture_text: str) -> Dict[str, Any]:
        """Returns: {'biblical_context': str, 'simple_explanation': str, 'spiritual_reflection': str, 'practical_application': str, 'optional_prayer': str, 'ai_generated': bool}"""
        pass

    @abstractmethod
    def devotional_for_emotion(self, emotion_name: str, reference_display: str, scripture_text: str) -> Dict[str, Any]:
        """Returns: {'title': str, 'reflection': str, 'practical_application': str, 'guiding_question': str, 'prayer': str, 'ai_generated': bool}"""
        pass

    @abstractmethod
    def generate_reflection(self, date: str) -> Dict[str, Any]:
        """Returns: {'title': str, 'scripture_reference': str, 'scripture_text': str, 'reflection_body': str, 'guiding_question': str, 'closing_prayer': str, 'ai_generated': bool}"""
        pass
