from abc import ABC, abstractmethod
from typing import Dict, Any

class AIService(ABC):
    @abstractmethod
    def explain_passage(self, reference_normalized: str, reference_display: str) -> Dict[str, Any]:
        """Returns: {'explanation': str, 'ai_generated': bool}"""
        pass

    @abstractmethod
    def devotional_for_emotion(self, emotion_name: str) -> Dict[str, Any]:
        """Returns: {'title': str, 'scripture_reference': str, 'scripture_text': str, 'reflection': str, 'prayer': str, 'ai_generated': bool}"""
        pass

    @abstractmethod
    def generate_reflection(self, date: str) -> Dict[str, Any]:
        """Returns: {'title': str, 'scripture_reference': str, 'scripture_text': str, 'reflection_body': str, 'guiding_question': str, 'closing_prayer': str, 'ai_generated': bool}"""
        pass
