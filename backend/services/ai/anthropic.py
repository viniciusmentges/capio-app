import json
import logging
from typing import Dict, Any
from django.conf import settings
from .base import AIService
from .mock import MockAIService

logger = logging.getLogger(__name__)

# Try to import anthropic, fallback if not installed yet
try:
    import anthropic
except ImportError:
    anthropic = None

class AnthropicAIService(AIService):
    def __init__(self):
        self.mock_fallback = MockAIService()
        self.api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
        self.model = getattr(settings, 'ANTHROPIC_MODEL', 'claude-haiku-4-5-20251001')
        
        if anthropic and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("Anthropic client not initialized. Missing API key or package.")

    def _get_base_constitution(self) -> str:
        return (
            "IDENTIDADE: Você é o MOTOR EDITORIAL DA CAPIO. Você não é um chatbot, não é um assistente e não é um coach espiritual. "
            "Você é um pipeline silencioso que compõe experiências contemplativas estruturadas.\n\n"
            "REGRAS DE OURO:\n"
            "1. SCRIPTURE-FIRST: A Palavra é o centro. Sua interpretação deve iluminar o texto, nunca substituí-lo.\n"
            "2. DESAPARECIMENTO DA IA: Não use 'eu', 'nós' ou frases auto-referenciais (ex: 'espero que ajude', 'vamos meditar').\n"
            "3. GRAMÁTICA DO SILÊNCIO: Proibido o uso de pontos de exclamação (!). Use apenas pontos finais e vírgulas.\n"
            "4. ECONOMIA DE LINGUAGEM: Frases curtas (máx 15 palavras). Máximo de 2 adjetivos por parágrafo.\n"
            "5. TONE: Sóbrio, denso, pastoral, silencioso. Evite tons triunfalistas, motivacionais ou infantis.\n"
            "6. ANTI-COACH: Nunca dê ordens ('Faça isso', 'Mude sua vida'). Use o modo convite ('O convite é...', 'Há um espaço para...').\n"
            "7. TERMINAÇÃO ABERTA: Não feche o pensamento com conclusões absolutas. Deixe espaço para o mistério.\n"
            "8. BLACKLIST: Proibido usar 'Jornada', 'Propósito', 'Vitória', 'Benção', 'Sucesso', 'Melhor versão', 'Como um modelo de linguagem'.\n"
            "9. FORMATO: Responda APENAS em JSON válido, sem texto markdown em volta."
        )

    def _call_claude(self, prompt: str, system_prompt: str, temperature: float, fallback_func, fallback_args: dict, expected_keys: list = None, max_tokens: int = 1500) -> Dict[str, Any]:
        if not self.client:
            return fallback_func(**fallback_args)
            
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text.strip()
            
            if content.startswith('```json'):
                content = content.replace('```json', '', 1)
            if content.endswith('```'):
                content = content[:-3]
                
            content = content.strip()
            data = json.loads(content)
            
            if expected_keys:
                for key in expected_keys:
                    if key not in data:
                        logger.error(f"Missing key '{key}' in AI response.")
                        return fallback_func(**fallback_args)
            
            data['ai_generated'] = True
            return data
            
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            return fallback_func(**fallback_args)



    def explain_passage(self, reference_normalized: str, reference_display: str) -> Dict[str, Any]:
        system_prompt = self._get_base_constitution() + (
            "\n\nCOMPOSER.EXEGESIS: Iluminação da Palavra. Foco em profundidade contemplativa e contexto."
        )
        prompt = (
            f"Ilumine a passagem: '{reference_display}'.\n"
            "Retorne UM objeto JSON com:\n"
            "- 'scripture_text': O texto bíblico exato da passagem.\n"
            "- 'biblical_context': O contexto histórico e o encontro original da passagem.\n"
            "- 'simple_explanation': O coração teológico em linguagem simples.\n"
            "- 'spiritual_reflection': Meditação sobre o mistério revelado.\n"
            "- 'practical_application': O 'Eco na Vida' - como esta Palavra vibra hoje.\n"
            "- 'optional_prayer': Oração curta de recolhimento."
        )
        return self._call_claude(
            prompt, system_prompt, 0.3,
            self.mock_fallback.explain_passage, 
            {"reference_normalized": reference_normalized, "reference_display": reference_display},
            expected_keys=['scripture_text', 'biblical_context', 'simple_explanation', 'spiritual_reflection', 'practical_application', 'optional_prayer']
        )


    def devotional_for_emotion(self, emotion_name: str) -> Dict[str, Any]:
        system_prompt = self._get_base_constitution() + (
            "\n\nCOMPOSER.DEVOTIONAL: Acolhimento pastoral da alma. Foco em empatia e condução à Palavra."
        )
        prompt = (
            f"Componha um devocional para o estado de alma: '{emotion_name}'.\n"
            "Retorne UM objeto JSON com:\n"
            "- 'title': Título poético e breve.\n"
            "- 'scripture_reference': Passagem que serve de abrigo.\n"
            "- 'scripture_text': O texto da Palavra.\n"
            "- 'reflection': Reflexão densa e silenciosa.\n"
            "- 'practical_application': Um gesto humano pequeno e concreto.\n"
            "- 'guiding_question': Pergunta para o silêncio da alma.\n"
            "- 'prayer': Oração de entrega."
        )
        return self._call_claude(
            prompt, system_prompt, 0.4,
            self.mock_fallback.devotional_for_emotion,
            {"emotion_name": emotion_name},
            expected_keys=['title', 'scripture_reference', 'scripture_text', 'reflection', 'practical_application', 'guiding_question', 'prayer']
        )

    def generate_reflection(self, date: str) -> Dict[str, Any]:
        system_prompt = self._get_base_constitution() + (
            "\n\nCOMPOSER.REFLECTION: Abertura contemplativa do dia. Foco em desacelerar e criar presença."
        )
        prompt = (
            f"Componha a Reflexão do Dia para: '{date}'.\n"
            "Retorne UM objeto JSON com:\n"
            "- 'title': Título contemplativo.\n"
            "- 'scripture_reference': A passagem guia de hoje.\n"
            "- 'scripture_text': O texto da Palavra.\n"
            "- 'reflection_body': Meditação calma (máx 1000 caracteres).\n"
            "- 'guiding_question': Pergunta para carregar no coração.\n"
            "- 'closing_prayer': Oração de encerramento."
        )
        return self._call_claude(
            prompt, system_prompt, 0.6,
            self.mock_fallback.generate_reflection,
            {"date": date},
            expected_keys=['title', 'scripture_reference', 'scripture_text', 'reflection_body', 'guiding_question', 'closing_prayer']
        )


