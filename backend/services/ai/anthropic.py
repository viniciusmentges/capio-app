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
            self.client = anthropic.Anthropic(api_key=self.api_key, timeout=6.0)
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

    def _call_claude(self, prompt: str, system_prompt: str, temperature: float, fallback_func, fallback_args: dict, expected_keys: list = None, max_tokens: int = 1500, ai_request_id: int = None, endpoint_origin: str = None) -> Dict[str, Any]:
        if not self.client:
            return fallback_func(**fallback_args)
            
        import time
        import hashlib
        from decimal import Decimal
        
        start_time = time.time()
        response = None
        
        try:
            # Tenta chamada com Prompt Caching (especificação de blocos de sistema da Anthropic)
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=[
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"}
                        }
                    ],
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
            except Exception as cache_err:
                logger.warning(
                    "[CAPIO Prompt Caching] Prompt Caching não suportado ou SDK/modelo incompatível. "
                    "Recorrendo à chamada padrão sem cache. Erro: %s", cache_err
                )
                # Fallback seguro para chamada padrão com string pura no system prompt
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
            duration_ms = int((time.time() - start_time) * 1000)
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
            
            # Captura de métricas reais da Anthropic
            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
            output_tokens = getattr(usage, "output_tokens", 0) if usage else 0
            
            # Detalhes específicos de Prompt Caching
            cache_creation_tokens = getattr(usage, "cache_creation_input_tokens", 0) if usage else 0
            cache_read_tokens = getattr(usage, "cache_read_input_tokens", 0) if usage else 0
            cache_hit = cache_read_tokens > 0
            
            # Cálculo do custo financeiro estimado operacional
            # Claude 3.5 Haiku: Input $0.80/M, Output $4.00/M, Cache Read $0.08/M, Cache Creation $1.00/M
            input_rate = 0.80 / 1_000_000
            output_rate = 4.00 / 1_000_000
            cache_read_rate = 0.08 / 1_000_000
            cache_creation_rate = 1.00 / 1_000_000
            
            model_lower = self.model.lower()
            if "sonnet" in model_lower:
                input_rate = 3.00 / 1_000_000
                output_rate = 15.00 / 1_000_000
                cache_read_rate = 0.30 / 1_000_000
                cache_creation_rate = 3.75 / 1_000_000
                
            standard_input_tokens = input_tokens - cache_creation_tokens - cache_read_tokens
            estimated_cost = (
                (standard_input_tokens * input_rate) +
                (cache_creation_tokens * cache_creation_rate) +
                (cache_read_tokens * cache_read_rate) +
                (output_tokens * output_rate)
            )
            
            # Injeta telemetria na resposta JSON para os consumidores
            if isinstance(data, dict):
                data['_ai_metrics'] = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "estimated_cost_usd": estimated_cost,
                    "duration_ms": duration_ms,
                    "model_name": self.model,
                    "endpoint_origin": endpoint_origin,
                    "cache_hit": cache_hit
                }
                
            # Persistência estruturada no modelo AIRequest do Django
            try:
                from apps.ai_core.models import AIRequest
                
                ai_req_obj = None
                if ai_request_id:
                    ai_req_obj = AIRequest.objects.filter(id=ai_request_id).first()
                    
                if not ai_req_obj:
                    h = hashlib.sha256(f"{self.model}:{prompt[:50]}".encode()).hexdigest()
                    ai_req_obj = AIRequest.objects.create(
                        request_type="bible" if expected_keys and "biblical_context" in expected_keys else "devotional",
                        input_hash=h,
                        input_data={"prompt": prompt[:500]},
                        status="pending"
                    )
                    
                ai_req_obj.status = "success"
                ai_req_obj.input_tokens = input_tokens
                ai_req_obj.output_tokens = output_tokens
                ai_req_obj.estimated_cost_usd = Decimal(str(round(estimated_cost, 10)))
                ai_req_obj.duration_ms = duration_ms
                ai_req_obj.model_name = self.model
                ai_req_obj.endpoint_origin = endpoint_origin or ai_req_obj.request_type
                ai_req_obj.cache_hit = cache_hit
                ai_req_obj.output_data = data
                ai_req_obj.save()
            except Exception as db_err:
                logger.error("[CAPIO TOKEN AUDIT] Falha ao persistir telemetria do Claude no AIRequest: %s", db_err)
                
            # Log bonito estruturado no console
            logger.info(
                "\n[CAPIO TOKEN AUDIT] =========================================="
                "\n* Origem: %s"
                "\n* Modelo: %s"
                "\n* Duração: %d ms"
                "\n* Input Tokens: %d (Cache Read: %d, Cache Created: %d)"
                "\n* Output Tokens: %d"
                "\n* Cache Hit: %s"
                "\n* Custo Estimado: $%0.10f USD"
                "\n==============================================================",
                endpoint_origin or "n/a",
                self.model,
                duration_ms,
                input_tokens,
                cache_read_tokens,
                cache_creation_tokens,
                output_tokens,
                "SIM" if cache_hit else "NÃO",
                estimated_cost
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            
            # Gravação segura de erro no AIRequest
            try:
                from apps.ai_core.models import AIRequest
                if ai_request_id:
                    ai_req_obj = AIRequest.objects.filter(id=ai_request_id).first()
                    if ai_req_obj:
                        ai_req_obj.status = "error"
                        ai_req_obj.output_data = {"error": str(e)}
                        ai_req_obj.save()
            except Exception as db_err:
                logger.error("[CAPIO TOKEN AUDIT] Falha ao persistir erro do Claude no AIRequest: %s", db_err)
                
            return fallback_func(**fallback_args)

    def explain_passage(self, reference_normalized: str, reference_display: str, scripture_text: str, ai_request_id: int = None) -> Dict[str, Any]:
        system_prompt = self._get_base_constitution() + (
            "\n\nCOMPOSER.EXEGESIS: Iluminação da Palavra. Foco em profundidade contemplativa e contexto."
            "\nBaseie a reflexão EXCLUSIVAMENTE na passagem fornecida."
        )
        prompt = (
            f"Passagem Bíblica Guia: {reference_display}\n"
            f"Texto Bíblico: \"{scripture_text}\"\n\n"
            "Retorne UM objeto JSON com os seguintes campos (todos em português):\n"
            "- 'biblical_context': O contexto histórico e o encontro original da passagem (máx 300 caracteres).\n"
            "- 'simple_explanation': O coração teológico em linguagem simples, sóbria e contemplativa.\n"
            "- 'spiritual_reflection': Meditação sobre o mistério revelado e silêncio da alma.\n"
            "- 'practical_application': O 'Eco na Vida' - como esta Palavra vibra hoje em silêncio e presença.\n"
            "- 'optional_prayer': Oração curta de recolhimento (sem pontos de exclamação)."
        )
        res = self._call_claude(
            prompt, system_prompt, 0.3,
            self.mock_fallback.explain_passage, 
            {"reference_normalized": reference_normalized, "reference_display": reference_display, "scripture_text": scripture_text},
            expected_keys=['biblical_context', 'simple_explanation', 'spiritual_reflection', 'practical_application', 'optional_prayer'],
            ai_request_id=ai_request_id,
            endpoint_origin="BIBLE_EXEGESIS"
        )
        res['scripture_text'] = scripture_text
        return res

    def devotional_for_emotion(self, emotion_name: str, reference_display: str, scripture_text: str, ai_request_id: int = None) -> Dict[str, Any]:
        system_prompt = self._get_base_constitution() + (
            "\n\nCOMPOSER.DEVOTIONAL: Acolhimento pastoral da alma. Foco em empatia e condução à Palavra."
            "\nBaseie o devocional EXCLUSIVAMENTE na passagem e no estado de alma fornecidos."
        )
        prompt = (
            f"Estado de Alma (Emoção): {emotion_name}\n"
            f"Passagem Bíblica Guia: {reference_display}\n"
            f"Texto Bíblico: \"{scripture_text}\"\n\n"
            "Retorne UM objeto JSON com os seguintes campos (todos em português):\n"
            "- 'title': Título poético e breve.\n"
            "- 'reflection': Reflexão pastoral densa, consoladora e silenciosa baseada no texto bíblico fornecido.\n"
            "- 'practical_application': Um gesto humano pequeno e concreto para acalmar a alma.\n"
            "- 'guiding_question': Pergunta íntima para o silêncio do coração.\n"
            "- 'prayer': Oração de entrega silenciosa (sem pontos de exclamação)."
        )
        res = self._call_claude(
            prompt, system_prompt, 0.4,
            self.mock_fallback.devotional_for_emotion,
            {"emotion_name": emotion_name, "reference_display": reference_display, "scripture_text": scripture_text},
            expected_keys=['title', 'reflection', 'practical_application', 'guiding_question', 'prayer'],
            ai_request_id=ai_request_id,
            endpoint_origin="EMOTIONAL_DEVOTIONAL"
        )
        res['scripture_reference'] = reference_display
        res['scripture_text'] = scripture_text
        return res

    def generate_reflection(self, date: str, ai_request_id: int = None) -> Dict[str, Any]:
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
            "- 'closing_prayer': Oração de encerramento.\n"
            "- 'share_quote': Um fragmento contemplativo de altíssimo valor editorial (máx 15 palavras) inspirado ou extraído da própria reflexão. Deve parecer um trecho grifado de um clássico espiritual ou anotação íntima de um monge, nunca uma frase de feed ou postagem motivacional de Instagram.\n\n"
            "REGRAS ESTRITAS DE ARQUITETURA PARA 'share_quote':\n"
            "1. LINGUAGEM DE LIVRO: Use palavras densas, sóbrias e humanas. Deve evocar silêncio, presença, espera, interioridade e descanso espiritual.\n"
            "2. PROIBIÇÃO DE AUTOAJUDA/COACHING: Banido imperativos (não use 'lembre-se', 'busque', 'confie', 'mude'). Banido jargões gospel ('Deus vai fazer', 'vitória', 'jornada', 'bênção').\n"
            "3. ZERO PONTUAÇÃO EXCESSIVA: Proibido absolutamente o uso de exclamações (!). Use apenas pontos e vírgulas.\n"
            "4. RITMO E COMPRIMENTO: Curto e memorável sem ser clichê. Máximo de 15 palavras. Frase limpa, sem aspas adicionais dentro da string."
        )
        return self._call_claude(
            prompt, system_prompt, 0.6,
            self.mock_fallback.generate_reflection,
            {"date": date},
            expected_keys=['title', 'scripture_reference', 'scripture_text', 'reflection_body', 'guiding_question', 'closing_prayer', 'share_quote'],
            ai_request_id=ai_request_id,
            endpoint_origin="DAILY_REFLECTION"
        )

    def editorial_generate_devotional(self, emotion_name: str, tone_or_direction: str = None, ai_request_id: int = None) -> Dict[str, Any]:
        system_prompt = self._get_base_constitution() + (
            "\n\nCOMPOSER.EDITORIAL: Você é o MOTOR EDITORIAL DE ASSISTÊNCIA DA CAPIO.\n"
            "Sua tarefa é compor um devocional contemplativo de altíssimo valor literário e pastoral baseado em uma emoção específica e uma direção espiritual."
        )
        
        prompt = (
            f"Escolha e componha um devocional contemplativo para a Emoção: '{emotion_name}'.\n"
        )
        if tone_or_direction:
            prompt += f"Direção Espiritual / Tom Desejado pelo Editor: '{tone_or_direction}'.\n"
            
        prompt += (
            "\nRetorne UM objeto JSON com os seguintes campos (todos em português):\n"
            "- 'title': Um título breve, sóbrio e contemplativo.\n"
            "- 'scripture_reference': A referência bíblica de uma passagem profunda e consoladora que você mesmo selecionou especificamente para este contexto (ex: 'Salmos 23:1-3').\n"
            "- 'scripture_text': O texto exato da passagem bíblica selecionada.\n"
            "- 'reflection': Uma reflexão pastoral densa, consoladora e silenciosa (máx 1000 caracteres). Deve parecer um trecho de um clássico espiritual tradicional ou o diário íntimo de um monge. Evite clichês modernos, tons triumfalistas ou performáticos.\n"
            "- 'prayer': Uma oração curta de entrega e recolhimento silencioso (sem exclamações).\n"
            "- 'share_quote': Um fragmento contemplativo curado de altíssimo valor editorial (máx 15 palavras) extraído ou inspirado na reflexão. Deve evocar interioridade, espera e silêncio. Proibido imperativos, jargões ou exclamações.\n"
            "- 'emotional_theme': Um subtema emocional curto que sintetiza a abordagem (ex: 'A quietude na espera').\n\n"
            "DIRETRIZES ESTRITAS DE CONSTITUIÇÃO CROMÁTICA E EDITORIAL:\n"
            "1. PROIBIÇÃO DE AUTOAJUDA / COACHING / TRIUNFALISMO: Banido imperativos (não use 'lembre-se', 'busque', 'confie', 'mude', 'não desista'). Banido jargões de prosperidade ou vitória ('vitória', 'bênção', 'prosperidade', 'Deus vai te dar').\n"
            "2. GRAMÁTICA DO SILÊNCIO: Proibido absolutamente o uso de pontos de exclamação (!). Use apenas pontos e vírgulas.\n"
            "3. SOBRIEDADE E PRESENÇA: O tom deve ser sóbrio, íntimo, acolhedor e com economia de palavras. Deixe espaço para o mistério e a espera silenciosa.\n"
            "4. FORMATO: Responda APENAS em JSON válido, sem texto markdown ou explicações externas."
        )
        
        return self._call_claude(
            prompt, system_prompt, 0.4,
            self.mock_fallback.editorial_generate_devotional,
            {"emotion_name": emotion_name, "tone_or_direction": tone_or_direction},
            expected_keys=['title', 'scripture_reference', 'scripture_text', 'reflection', 'prayer', 'share_quote', 'emotional_theme'],
            ai_request_id=ai_request_id,
            endpoint_origin="EDITORIAL_GENERATOR"
        )

    def generate_share_quote(self, reflection: str, ai_request_id: int = None) -> str:
        # Prompt secundário minimalista modularizado! Reduz tokens de entrada em >500 tokens por chamada!
        system_prompt = (
            "Você é o Diretor Editorial da CAPIO. Sua missão é extrair ou formular um fragmento contemplativo "
            "de no máximo 15 palavras com base na reflexão fornecida. Esse fragmento servirá para o card de imagem compartilhável."
        )
        prompt = (
            f"Gere um fragmento (share_quote) de no máximo 15 palavras para a meditação:\n\"{reflection}\"\n\n"
            "REGRAS CRÍTICAS:\n"
            "1. CONCISÃO: Máximo de 15 palavras. Curto e com densidade de livro clássico espiritual.\n"
            "2. ANTI-COACH: NUNCA use imperativos ('confie', 'lembre-se', 'mude'). Sem jargões gospel ('vitória', 'bênção').\n"
            "3. SILÊNCIO: Proibido o uso de pontos de exclamação (!). Use apenas pontos finais e vírgulas.\n"
            "4. RETORNO: Retorne um objeto JSON contendo exclusivamente a chave 'share_quote' (ex: {\"share_quote\": \"frase\"}), sem markdown."
        )

        res = self._call_claude(
            prompt, system_prompt, 0.4,
            self.mock_fallback.generate_share_quote,
            {"reflection": reflection},
            expected_keys=['share_quote'],
            ai_request_id=ai_request_id,
            endpoint_origin="SHARE_QUOTE"
        )
        return res.get('share_quote', "O silêncio é o solo fértil onde a graça de Deus repousa.")
