from django.conf import settings
from .base import AIService
from .mock import MockAIService

def get_ai_service() -> AIService:
    if getattr(settings, 'USE_REAL_AI', False):
        from .anthropic import AnthropicAIService
        return AnthropicAIService()
    return MockAIService()
