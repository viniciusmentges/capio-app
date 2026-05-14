from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from services.ai import get_ai_service
from services.ai.mock import MockAIService
from services.ai.anthropic import AnthropicAIService

class AIServiceTests(TestCase):
    
    @override_settings(USE_REAL_AI=False)
    def test_get_ai_service_returns_mock_by_default(self):
        service = get_ai_service()
        self.assertIsInstance(service, MockAIService)

    @override_settings(USE_REAL_AI=True, ANTHROPIC_API_KEY='test_key')
    def test_get_ai_service_returns_anthropic_when_configured(self):
        service = get_ai_service()
        self.assertIsInstance(service, AnthropicAIService)
        self.assertIsNotNone(service.client)

    @override_settings(USE_REAL_AI=True, ANTHROPIC_API_KEY='test_key')
    @patch('services.ai.anthropic.anthropic.Anthropic')
    def test_anthropic_service_fallback_on_api_error(self, MockAnthropic):
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        MockAnthropic.return_value = mock_client
        
        service = get_ai_service()
        
        # Call explain_passage
        result = service.explain_passage("joao 3:16", "João 3:16")
        
        # Should fallback to MockAIService which returns 'ai_generated': False
        self.assertIn('explanation', result)
        self.assertFalse(result.get('ai_generated', True))

    @override_settings(USE_REAL_AI=True, ANTHROPIC_API_KEY='test_key')
    @patch('services.ai.anthropic.anthropic.Anthropic')
    def test_anthropic_service_fallback_on_invalid_json(self, MockAnthropic):
        # Setup mock to return invalid JSON
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Isso não é um JSON válido")]
        mock_client.messages.create.return_value = mock_message
        MockAnthropic.return_value = mock_client
        
        service = get_ai_service()
        
        result = service.devotional_for_emotion("ansioso")
        
        self.assertIn('title', result)
        self.assertFalse(result.get('ai_generated', True))

    @override_settings(USE_REAL_AI=True, ANTHROPIC_API_KEY='test_key')
    @patch('services.ai.anthropic.anthropic.Anthropic')
    def test_anthropic_service_fallback_on_missing_keys(self, MockAnthropic):
        # Setup mock to return missing keys in JSON
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text='{"title": "Test"}')] # Missing other expected keys
        mock_client.messages.create.return_value = mock_message
        MockAnthropic.return_value = mock_client
        
        service = get_ai_service()
        
        result = service.devotional_for_emotion("ansioso")
        
        # Should fallback to mock
        self.assertIn('scripture_reference', result)
        self.assertFalse(result.get('ai_generated', True))
