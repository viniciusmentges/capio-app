import json
import logging
from typing import Dict, Any
from django.conf import settings
from .base import AIService
from .mock import MockAIService
from services.observability import capture_exception, log_event

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
            # Timeout elevado para suportar geração editorial (tipicamente 15–60s).
            # 6.0s anterior causava falha imediata no Prompt Caching e worker timeout no Gunicorn.
            self.client = anthropic.Anthropic(api_key=self.api_key, timeout=120.0)
        else:
            self.client = None
            logger.warning("Anthropic client not initialized. Missing API key or package.")

    def _get_base_constitution(self) -> str:
        return (
            "IDENTIDADE: Você é o MOTOR EDITORIAL DA CAPIO. Você não é um chatbot, não é um assistente e não é um coach espiritual. "
            "Você é um pipeline silencioso que compõe experiências contemplativas e sóbrias estruturadas.\n\n"
            "REGRAS DE OURO:\n"
            "1. SCRIPTURE-FIRST: A Palavra é o centro. Sua interpretação deve iluminar o texto, nunca substituí-lo.\n"
            "2. CLAREZA ACIMA DA ELEGÂNCIA: Sempre preferir a frase que comunica melhor sobre construções poéticas obscuras. Teste da Avó: uma senhora de 70 anos deve compreender na primeira leitura. Toda frase deve sobreviver sozinha (independência semântica).\n"
            "3. DESAPARECIMENTO DA IA: Não use 'eu', 'nós' ou frases auto-referenciais.\n"
            "4. PONTUAÇÃO E INTERROGAÇÕES: Proibido absolutamente o uso de pontos de exclamação (!). Interrogações (?) são permitidas com moderação para condução reflexiva pastoral, proibidas para criar urgência ou marketing.\n"
            "5. ECONOMIA DE LINGUAGEM E METÁFORAS: Frases curtas (máx 15 palavras). Máximo de 2 adjetivos por parágrafo. ECONOMIA DE METÁFORAS: apenas uma metáfora principal por parágrafo; evite acumular símbolos soltos (deserto, travessia, jornada, tempestade).\n"
            "6. TONE: Reverente, sóbrio, denso, pastoral, silencioso. Evite tons triunfalistas, motivacionais ou infantis.\n"
            "7. ANTI-COACH: Nunca dê ordens ('Faça isso', 'Mude sua vida'). Use o modo convite ('O convite é...', 'Há um espaço para...').\n"
            "8. O ECO DA PALAVRA: A reflexão não existe para transmitir muitas ideias, mas para conduzir o leitor até uma única verdade central da Escritura ('Qual foi a principal verdade que Deus colocou diante de mim hoje?'). Um único centro de gravidade.\n"
            "9. TESTE DO SUBLINHADO: Toda reflexão deve conter pelo menos uma frase memorável e verdadeira que o leitor sublinharia se tivesse um lápis nas mãos.\n"
            "10. A VOZ DA CAPIO: Escrever para acompanhar, não para impressionar. Ordem de inspiração: 1. Evangelhos (Jesus); 2. C. S. Lewis; 3. Tim Keller; 4. Henri Nouwen. Místicos apenas atmosfera. TESTE DA CONVERSA: Soaria natural num café entre amigos?\n"
            "11. O SHARE QUOTE: Não é resumo, legenda ou frase bonita. É o pensamento que continua acompanhando o leitor depois que ele fecha a CAPIO, apontando para a Escritura.\n"
            "12. OBJETIVO FINAL: A tecnologia, o design e a escrita devem desaparecer, permanecendo apenas a Escritura ecoando silenciosamente durante o restante do dia.\n"
            "13. BLACKLIST: Proibido 'Vitória triunfalista', 'Melhor versão'.\n"
            "14. FORMATO: Responda APENAS em JSON válido, sem texto markdown em volta."
        )

    def _get_editorial_constitution(self) -> str:
        """Prompt de sistema compacto exclusivo do motor editorial.
        Otimizado para clareza humana, anti-abstração e token economy."""
        return (
            "Motor Editorial da CAPIO. Não é chatbot. Não é narrador espiritual abstrato.\n\n"
            "REGRAS INVIOLÁVEIS:\n"
            "1. SCRIPTURE-FIRST: A Palavra é o centro. Iluminar, nunca substituir.\n"
            "2. HUMANIDADE CONCRETA: O texto nasce de experiência humana real e reconhecível.\n"
            "3. CLAREZA PRIORITÁRIA: Clareza acima da Elegância. Teste da Avó. Toda frase deve sobreviver sozinha.\n"
            "4. O ECO DA PALAVRA & METÁFORAS: Apenas uma verdade central por reflexão. Máximo de 1 metáfora dominante por parágrafo.\n"
            "5. REGRA DA COERÊNCIA INVISÍVEL: Os quatro campos formam uma única jornada: Reflection -> Fio da Palavra -> Palavra Continua -> Share Quote. Cada um conduz o leitor um passo adiante: nunca resume o anterior, nunca antecipa o próximo.\n"
            "6. IDENTIDADE DOS CAMPOS:\n"
            "   - Reflection: Conduz.\n"
            "   - Fio da Palavra (main_truth): Ancora. Uma única verdade.\n"
            "   - Palavra Continua (daily_companion): Acompanha. Sem ordens, sem conselhos, sem mandar. Caminha junto.\n"
            "   - Share Quote: Permanece. Não é gerado, é descoberto. A frase que continua ecoando depois que o restante desaparece.\n"
            "7. REGRA DO LÁPIS ESPONTÂNEO (SHARE QUOTE): Qual frase faria alguém parar a leitura e pensar: 'preciso enviar isso para alguém que amo?' O Share Quote é a frase que um leitor destacaria espontaneamente a lápis. Nunca criada para marketing ou redes sociais. Responda internamente: 'Essa frase existiria mesmo se ninguém fosse compartilhá-la?'.\n"
            "8. AUDITORIA FINAL SILENCIOSA: Antes de aprovar, responda: 'Este texto parece escrito por alguém que deseja impressionar ou por alguém que deseja acompanhar?' Se houver qualquer traço de performance literária, reescreva. A beleza deve servir à Palavra, nunca competir com ela.\n"
            "9. A VOZ DA CAPIO: Ordem: 1. Evangelhos (Jesus); 2. C. S. Lewis; 3. Tim Keller; 4. Henri Nouwen. Místicos apenas atmosfera. TESTE DA CONVERSA: Soaria natural num café?\n"
            "10. SEM AUTORREFERÊNCIA: Proibido 'eu', 'nós'. Proibido (!).\n"
            "11. FRASES CURTAS: Máx 15 palavras. Sem imperativos apressados.\n"
            "12. OBJETIVO FINAL: Tudo deve desaparecer para ficar apenas a Escritura ecoando no leitor.\n"
            "13. FORMATO: Responda APENAS em JSON válido, sem markdown."
        )

    def _call_claude(self, prompt: str, system_prompt: str, temperature: float, fallback_func, fallback_args: dict, expected_keys: list = None, max_tokens: int = 1500, ai_request_id: int = None, endpoint_origin: str = None) -> Dict[str, Any]:
        if not self.client:
            log_event("ai_fallback_used", request_type=endpoint_origin or "unknown", fallback="mock_ai_service")
            return fallback_func(**fallback_args)
            
        import time
        import hashlib
        from decimal import Decimal
        
        start_time = time.time()
        response = None
        
        try:
            log_event("ai_request_started", request_type=endpoint_origin or "unknown", model_name=self.model)
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

            log_event(
                "ai_request_success",
                request_type=endpoint_origin or "unknown",
                model_name=self.model,
                duration_ms=duration_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost_usd=estimated_cost,
                cache_hit=cache_hit,
            )
            log_event("cache_hit" if cache_hit else "cache_miss", request_type=endpoint_origin or "unknown", cache_layer="anthropic_prompt_cache")
                
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
            capture_exception(e, event="ai_request_failed", request_type=endpoint_origin or "unknown", model_name=self.model)
            log_event("ai_request_failed", request_type=endpoint_origin or "unknown", model_name=self.model, error_type=type(e).__name__)
            
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

    def generate_reading_focus(self, chapter_text: str, reference_display: str, verse_start: int, verse_end: int, ai_request_id: int = None) -> Dict[str, Any]:
        system_prompt = self._get_base_constitution() + (
            "\n\nCOMPOSER.FOCUS: Iluminação pontual de trechos específicos da Palavra. Foco em profundidade contemplativa e simplicidade pastoral."
        )
        prompt = (
            f"Capítulo Bíblico Guia (Contexto): \"{chapter_text}\"\n\n"
            f"Trecho Focado: {reference_display}\n\n"
            "Ilumine o trecho focado à luz do capítulo inteiro. "
            "Retorne UM objeto JSON com os seguintes campos:\n"
            "- 'title': Título curto, por padrão use 'O foco desta leitura' ou variação sutil.\n"
            "- 'content': Um texto breve, contemplativo e pastoral (entre 80 e 150 palavras) que explique o trecho focado.\n\n"
            "Restrições:\n"
            "- Não gere oração, contexto completo, eco, ou reflexão longa.\n"
            "- Não repita explicações gerais do capítulo."
        )
        res = self._call_claude(
            prompt, system_prompt, 0.3,
            self.mock_fallback.generate_reading_focus, 
            {"chapter_text": chapter_text, "reference_display": reference_display, "verse_start": verse_start, "verse_end": verse_end},
            expected_keys=['title', 'content'],
            ai_request_id=ai_request_id,
            endpoint_origin="READING_FOCUS"
        )
        return res

    def devotional_for_emotion(
        self,
        emotion_name: str,
        reference_display: str,
        scripture_text: str,
        ai_request_id: int = None,
        excluded_passages: list = None,
        excluded_themes: list = None,
        excluded_titles: list = None,
        semantic_cooldown_words: list = None,
    ) -> Dict[str, Any]:
        system_prompt = self._get_editorial_constitution()

        emotion_key = emotion_name.lower().strip()
        emotion_key = emotion_key.replace(",", "").replace(".", "").replace("ç", "c").replace("ã", "a").replace("é", "e").replace("í", "i").replace("ó", "o")
        emotion_key = emotion_key.replace(" ", "-").replace("_", "-")

        import random
        angles = self._EDITORIAL_EMOTION_ANGLES.get(emotion_key, [])
        chosen_angle = random.choice(angles) if angles else f"experiência vivida, humana e concreta de {emotion_name}"

        style_key, style_instruction = self._pick_opening_style()
        logger.info(
            "[CAPIO OPENING STYLE AUDIT] Emoção '%s' — estilo de abertura selecionado: '%s' | Ângulo: '%s'",
            emotion_name, style_key, chosen_angle
        )

        all_excluded_passages = set(self._EDITORIAL_PASSAGE_BLACKLIST.get(emotion_key, []))
        if excluded_passages:
            all_excluded_passages.update(excluded_passages)

        prompt = (
            f"Emoção: {emotion_name}\n"
            f"Passagem Bíblica Guia: {reference_display}\n"
            f"Texto Bíblico: \"{scripture_text}\"\n"
        )

        if all_excluded_passages:
            prompt += "\n[PROIBIDO] ABORDAGENS/PASSAGENS JÁ EXPLORADAS (evite repetir tons idênticos):\n"
            prompt += "".join(f"  - {p}\n" for p in sorted(all_excluded_passages))

        if excluded_themes:
            prompt += "\n[PROIBIDO] TEMAS PROIBIDOS (já usados recentemente):\n"
            prompt += "".join(f"  - {t}\n" for t in excluded_themes)

        if excluded_titles:
            prompt += "\n[PROIBIDO] TITULOS PROIBIDOS:\n"
            prompt += "".join(f"  - {ti}\n" for ti in excluded_titles)

        if semantic_cooldown_words:
            prompt += "\n[RESFRIAMENTO SEMÂNTICO] Estas palavras saturaram os últimos devocionais. Evite-as absolutamente:\n"
            prompt += "".join(f"  - {w}\n" for w in semantic_cooldown_words)

        prompt += (
            f"\n[ANGULO HUMANO OBRIGATORIO]\n"
            f"Experiência humana concreta para esta meditação: \"{chosen_angle}\"\n"
            f"(Sua reflexão DEVE construir ao redor desta experiência humana específica, sem tentar cobrir todos os aspectos de {emotion_name}. O leitor deve se reconhecer antes de qualquer elaboração teológica).\n\n"
            f"[ABERTURA]\n"
            f"Estilo obrigatório para iniciar a reflexão:\n{style_instruction}\n"
            f"Proibido começar com \"Há momentos em que...\", \"Quando a vida...\", \"Todos nós...\" ou estruturas espelhadas.\n\n"
            "Retorne UM objeto JSON com os seguintes campos (todos em português):\n"
            "- 'title': Título sóbrio e específico. Humano, não poético demais.\n"
            "- 'reflection': Reflection. CONDUZ. Responde a: 'O que Deus revelou nesta passagem?'. Conduz o leitor da experiência humana concreta até a Escritura. Não precisa explicar tudo nem fechar tudo; abra espaço para contemplação. Entre 1200 e 1400 caracteres.\n"
            "- 'practical_application': Gesto humano pequeno e concreto. Não conselho abstrato.\n"
            "- 'guiding_question': Pergunta íntima nascida desta emoção específica. Sem respostas embutidas.\n"
            "- 'prayer': Oração honesta e curta. Nascida da experiência, não de fórmula. Sem exclamações (!).\n"
            "- 'main_truth': Fio da Palavra. ANCORA. Responde a: 'Qual é a verdade que sustenta todo este texto?'. Uma única verdade bíblica sem a qual este devocional deixaria de existir. Extremamente simples, profundamente bíblica, memorável. NÃO É RESUMO nem conclusão.\n"
            "- 'daily_companion': Palavra Continua. ACOMPANHA. Responde a: 'O que permanecerá acompanhando o leitor hoje?'. A frase que caminha junto com o leitor às 15h da tarde. Sem dar ordens, sem aconselhar, sem mandar (proibido imperativos!). É uma companhia silenciosa que cabe inteira na memória.\n"
            "- 'share_quote': Share Quote. PERMANECE. Não é gerado, é DESCOBERTO. Responde a: 'Qual frase faria alguém parar a leitura e pensar: preciso enviar isso para alguém que amo?'. REGRA DO LÁPIS ESPONTÂNEO: A frase que um leitor destacaria espontaneamente com um lápis durante a leitura. Nunca criada para virar imagem ou rede social. Antes de gerar, responda internamente: 1. 'Se este devocional fosse publicado em um livro, qual frase um leitor marcaria a lápis?'; 2. 'Essa frase existiria exatamente assim se ninguém pudesse compartilhá-la?'. Se não, reescreva. Máximo 15 palavras. Proibido: paralelismos, frases espelhadas, slogans. Sem exclamações (!).\n"
            "- 'emotional_theme': Max 5 palavras. Subtema humano direto para este ângulo.\n\n"
            "AUDITORIA ANTI-REDUNDÂNCIA E COERÊNCIA INVISÍVEL:\n"
            "Os quatro campos (Reflection -> Fio da Palavra -> Palavra Continua -> Share Quote) formam uma única experiência e jornada: cada um conduz um passo adiante, nunca resume o anterior, nunca antecipa o próximo.\n"
            "Antes de aprovar o JSON, responda internamente:\n"
            "1. 'Se eu remover completamente a Reflection... Os outros campos continuam fazendo sentido sozinho?' Se sim, estão grandes demais.\n"
            "2. 'Se eu remover o Share Quote... O devocional perde algo?' Se não, o Share Quote está fraco.\n"
            "3. 'Se o Daily Companion repetir o Main Truth:' Reescreva. Nenhum campo pode existir apenas para repetir outro.\n"
            "4. AUDITORIA FINAL: 'Este texto parece escrito por alguém que deseja impressionar ou por alguém que deseja acompanhar?' Se houver traço de performance literária, reescreva. A beleza deve servir à Palavra, nunca competir com ela."
        )
        res = self._call_claude(
            prompt, system_prompt, 0.4,
            self.mock_fallback.devotional_for_emotion,
            {"emotion_name": emotion_name, "reference_display": reference_display, "scripture_text": scripture_text},
            expected_keys=['title', 'reflection', 'practical_application', 'guiding_question', 'prayer', 'share_quote', 'main_truth', 'daily_companion'],
            ai_request_id=ai_request_id,
            endpoint_origin="EMOTIONAL_DEVOTIONAL"
        )
        res['scripture_reference'] = reference_display
        res['scripture_text'] = scripture_text
        return res

    def generate_reflection(
        self,
        date: str,
        theme: dict = None,
        excluded_passages: list = None,
        semantic_cooldown: list = None,
        ai_request_id: int = None,
    ) -> Dict[str, Any]:
        system_prompt = self._get_base_constitution() + (
            "\n\nCOMPOSER.REFLECTION: Composição da abertura do dia. "
            "O tom é contemplativo e pastoral. O tema deve emergir da Escritura selecionada, não de um arquétipo tonal fixo. "
            "A reflexão pode ser serena, firme, de coragem, de entrega, pastoral ou narrativa — o que a Palavra pede hoje."
        )
        prompt = f"Componha a Reflexão do Dia para: '{date}'.\n\n"

        if theme:
            prompt += f"\n[EIXO TEMÁTICO DO DIA] {theme.get('label', '')}\n"
            prompt += f"Foco editorial: {theme.get('description', '')}\n"

            scripture_hints = theme.get("scripture_hints") or []
            if scripture_hints:
                prompt += "Passagens com afinidade:\n"
                for passage in scripture_hints:
                    prompt += f"- {passage}\n"
            prompt += "\n"

        if semantic_cooldown:
            prompt += "\n[RESFRIAMENTO SEMÂNTICO]\n"
            prompt += "Evite repetir como tema central os subtemas usados recentemente:\n"
            for item in semantic_cooldown:
                prompt += f"- {item}\n"
            prompt += "\n"

        if excluded_passages:
            prompt += "[PROIBIDO] Passagens já usadas recentemente — não repita nenhuma delas sob hipótese alguma:\n"
            prompt += "".join(f"  - {p}\n" for p in excluded_passages)
            prompt += "\n"

        prompt += (
            "INVERSÃO DA ARQUITETURA EDITORIAL (ORDEM LÓGICA OBRIGATÓRIA DE GERAÇÃO):\n"
            "1. Identifique primeiro a Verdade Central ('central_truth') da passagem bíblica.\n"
            "2. A partir dessa Verdade Central, escreve a Reflexão ('reflection_body'). Toda a reflexão deve nascer para conduzir o leitor até essa única verdade.\n"
            "3. Depois, escreve O Fio da Palavra ('main_truth').\n"
            "4. Por último, escreve A Palavra Continua ('daily_companion').\n\n"
            "Retorne UM objeto JSON com:\n"
            "- 'title': Título contemplativo e específico.\n"
            "- 'scripture_reference': A passagem guia de hoje (nunca repita as listadas no bloco [PROIBIDO] e priorize as recomendadas pelo EIXO TEMÁTICO se possível).\n"
            "- 'scripture_text': O texto da Palavra.\n"
            "- 'central_truth': A Verdade Central que orienta toda a leitura (apenas 1 frase simples).\n"
            "- 'reflection_body': Meditação profunda (máx 1000 caracteres). Começa no chão humano, encontra a Palavra, deixa espaço. ATENÇÃO: Não domesticar a reflexão do dia! A reflexão diurna deve preservar toda a força, tensão bíblica, profundidade e confronto saudável (honestidade espiritual, podendo falar de luta, obediência ativa, chamado, tentação, conflito interior e resistência). Não a torne artificialmente calma ou anestesiada.\n"
            "- 'main_truth': O Fio da Palavra (entre 2 e 3 frases; linguagem extremamente simples e profundamente bíblica; revela explicitamente a Verdade Central que orientou toda a construção do texto. NÃO é um resumo, NÃO é conclusão, NÃO é nova reflexão).\n"
            "- 'daily_companion': A Palavra Continua (ponte delicada entre a leitura e o restante do dia; acompanha o leitor nas próximas horas. NÃO é desafio, NÃO é tarefa, NÃO é lista de ações, NÃO é imperativo, NÃO funciona como checklist espiritual. Ex: 'Quando alguma preocupação surgir hoje, talvez esta passagem volte silenciosamente à sua memória.').\n"
            "- 'guiding_question': Pergunta para carregar no coração.\n"
            "- 'closing_prayer': Oração curta de encerramento da meditação DIURNA.\n"
            "- 'share_quote': Um fragmento ou eco memorável (máx 15 palavras) extraído ou inspirado na reflexão, próprio para um card compartilhável.\n"
            "- 'night_word': Crie uma frase NOVA, curta e contemplativa para a noite (Palavra da Noite). Ela deve ecoar o tema da reflexão do dia, mas NÃO DEVE repetir frases, imagens ou construções já usadas no texto principal ou no share_quote. Absolutamente proibida a cópia literal.\n"
            "- 'night_prayer': Crie uma oração curta de entrega, própria para o fim do dia. Ela deve nascer do mesmo tema espiritual, mas não repetir frases da reflexão diária nem da Palavra da Noite. Calibre-a estritamente para o repouso noturno: evite tensões ou confronto aqui. Deve inspirar confiança silenciosa, repouso, desaceleração, respiração, quietude e entrega de fim de dia no Senhor.\n"
            "- 'emotional_theme': Subtema em até 5 palavras, usado para rastreamento semântico.\n\n"
            "SEPARAÇÃO CLARA E EXCLUSIVIDADE DOS BLOCOS DIURNOS:\n"
            "Cada bloco possui uma função diferente. Nunca repetir ideias ou frases.\n"
            "- Reflexão: Explica. Conduz. Interioriza.\n"
            "- O Fio da Palavra: Destila. Revela a única verdade que permanece. Não resume. Não repete.\n"
            "- A Palavra Continua: Acompanha. Leva discretamente essa verdade para o dia. Nunca moraliza nem cobra.\n"
            "Caso qualquer bloco repita outro, a geração será considerada inválida.\n\n"
            "REGRAS ESTRITAS DE RITUAL NOTURNO PARA 'night_prayer' E 'night_word':\n"
            "1. DIREÇÃO DA NOITE: A noite não apaga o tema do dia; ela apenas o conduz suavemente ao silêncio, ao repouso e à permanência pacífica no Senhor.\n"
            "2. PROIBIÇÃO DE CONFRONTO E TENSÃO NA NOITE: A oração de encerramento e a palavra da noite devem focar em paz, descanso espiritual e respiração calma, sem acusações ou pressões.\n"
            "3. ANTI-REPETIÇÃO ESTRITA: A Palavra da Noite ('night_word') NÃO pode ser idêntica ou substring de 'reflection_body', 'title' ou 'share_quote'. A Oração da Noite ('night_prayer') NÃO pode copiar frases de 'closing_prayer'.\n\n"
            "REGRAS ESTRITAS DE ARQUITETURA PARA 'share_quote' E 'night_word':\n"
            "1. LINGUAGEM DE LIVRO: Use palavras densas, sóbrias e humanas. Não se limite apenas a 'silêncio, presença, espera' — expresse verdade e profundidade.\n"
            "2. PROIBIÇÃO DE AUTOAJUDA/COACHING: Banido imperativos (não use 'lembre-se', 'busque', 'confie', 'mude'). Banido jargões gospel ('Deus vai fazer', 'vitória', 'jornada', 'bênção').\n"
            "3. ZERO PONTUAÇÃO EXCESSIVA: Proibido absolutamente o uso de exclamações (!). Use apenas pontos e vírgulas.\n"
            "4. RITMO E COMPRIMENTO: Curtos e memoráveis sem serem clichês. Máximo de 15 palavras. Frase limpa, sem aspas adicionais dentro da string."
        )
        return self._call_claude(
            prompt, system_prompt, 0.75,
            self.mock_fallback.generate_reflection,
            {
                "date": date,
                "theme": theme,
                "excluded_passages": excluded_passages,
                "semantic_cooldown": semantic_cooldown,
            },
            expected_keys=[
                'title', 'scripture_reference', 'scripture_text', 'central_truth', 'reflection_body', 
                'main_truth', 'daily_companion', 'guiding_question', 'closing_prayer', 
                'share_quote', 'emotional_theme', 'night_word', 'night_prayer'
            ],
            ai_request_id=ai_request_id,
            endpoint_origin="DAILY_REFLECTION"
        )

    # Ângulos humanos específicos por emoção — partem da experiência vivida, não de conceitos espirituais.
    # Cada entrada descreve um estado interno real que o leitor pode reconhecer imediatamente.
    _EDITORIAL_EMOTION_ANGLES = {
        'ansioso': [
            "noite sem dormir — mente acelerada, pensamentos que não param às 2 da manhã",
            "aperto no peito antes de uma decisão, notícia ou conversa difícil",
            "excesso de responsabilidade — o peso de tudo que só você carrega",
            "pensamentos em loop — a mesma preocupação voltando sozinha",
            "medo do futuro — imaginando o pior antes de acontecer",
            "preocupação com alguém amado que não se pode proteger",
            "urgência sem objeto — pressa e agitação sem saber exatamente o quê",
            "cansaço mental de viver sempre em estado de alerta",
            "pressão interna — cobrança que vem de dentro, não de fora",
            "dificuldade de orar — palavras que não saem, Deus que parece distante",
            "ansiedade no corpo — ombros tensos, respiração curta, estômago fechado",
            "antecipação do pior — catastrofismo que precede o acontecimento",
        ],
        'triste': [
            "luto ainda sem nome — a perda recente que ainda não assentou",
            "saudade de algo que não volta mais",
            "choro que vem sem razão aparente",
            "solidão no meio das pessoas — estar cercado e não ser visto",
            "cansaço de precisar parecer bem para os outros",
            "decepção com alguém em quem se confiava",
            "sensação de vazio que nada parece preencher",
            "dor do fechamento de um ciclo importante",
        ],
        'medo': [
            "medo concreto de algo real e nomeável",
            "medo difuso — angústia sem objeto específico",
            "paralisia diante de uma decisão pelo medo de errar",
            "medo de decepcionar quem depende de você",
            "o próximo passo que não se consegue ver",
            "noite que amplia todos os medos",
        ],
        'sozinho': [
            "solidão física — estar genuinamente só, sem ninguém",
            "solidão emocional — estar com pessoas e não ser compreendido",
            "vazio deixado por quem partiu",
            "distância de quem se ama",
            "sensação de não pertencer a nenhum lugar",
            "madrugada sozinho — silêncio da casa que amplifica tudo",
        ],
        'desmotivado': [
            "acordar sem vontade — manhã pesada, cama que prende",
            "perda de sentido no trabalho ou na vida",
            "exaustão de quem tentou e não viu resultado",
            "indiferença emocional — quando nada parece importar",
            "peso físico que reflete o estado interior",
            "sensação de ficar para trás enquanto os outros avançam",
        ],
        'desesperançoso': [
            "manhã que não traz novidade — acordar e sentir que nada mudou",
            "perda de fé no futuro — quando não há como imaginar que melhora",
            "cansaço de esperar por algo que nunca parece chegar",
            "o esforço que não trouxe resultado — tentou e não funcionou",
            "orações que parecem não chegar a lugar nenhum",
            "impossibilidade de imaginar um amanhã diferente do hoje",
            "quando o que antes dava sentido à vida vai desaparecendo",
            "sensação de estar parado enquanto a vida passa",
        ],
        'corajoso-mas-incerto': [
            "a pessoa sabe o que precisa enfrentar, mas ainda sente medo",
            "coragem como obediência, não ausência de medo",
            "o primeiro passo parece pequeno, mas é real",
            "Deus não exige bravura performática",
            "firmeza nasce de confiança, não de autossuficiência",
        ],
        'chamado-mas-hesitante': [
            "a pessoa sente uma direção, mas teme o custo",
            "vocação pode começar como desconforto santo",
            "nem todo chamado vem com clareza total",
            "Deus conduz enquanto a pessoa caminha",
            "obediência parcial revela medo de perder controle",
        ],
        'tentado': [
            "tentação como luta real, não vergonha abstrata",
            "resistência começa na sujeição a Deus",
            "desejo desordenado promete alívio, mas cobra domínio",
            "fidelidade acontece no intervalo entre impulso e escolha",
            "Cristo entende a fraqueza sem romantizá-la",
        ],
        'em-conflito-com-alguem': [
            "perdão não apaga a dor, mas impede que ela governe",
            "reconciliação exige verdade, não fingimento",
            "a paz bíblica não é evitar conversa difícil",
            "orgulho espiritual pode se esconder atrás da razão",
            "amar o inimigo começa quando paramos de caricaturá-lo",
        ],
        'grato-mas-disperso': [
            "gratidão como atenção treinada",
            "a bondade de Deus pode ser ignorada pela pressa",
            "alegria não nasce da abundância de estímulos",
            "lembrar também é uma disciplina espiritual",
            "o coração cheio de coisas pode esquecer o Doador",
        ],
        'disciplinado-mas-frio': [
            "rotina espiritual sem amor vira mecanismo",
            "disciplina é caminho, não substituto da presença",
            "constância precisa permanecer viva diante de Deus",
            "o hábito pode proteger a chama ou escondê-la",
            "Deus deseja o coração, não apenas a prática correta",
        ],
    }

    # Passagens proibidas permanentemente por emoção — independentes do banco.
    # Usadas quando o viés do corpus força o modelo a retornar sempre a mesma passagem.
    _EDITORIAL_PASSAGE_BLACKLIST = {
        'ansioso':        ['Filipenses 4:6-7', 'Filipenses 4:6', 'Filipenses 4:7'],
        'medo':           [],
        'triste':         [],
        'sozinho':        [],
        'desmotivado':    [],
        'desesperançoso': [],
        'corajoso-mas-incerto': [],
        'chamado-mas-hesitante': [],
        'tentado': [],
        'em-conflito-com-alguem': [],
        'grato-mas-disperso': [],
        'disciplinado-mas-frio': [],
    }

    # Passagens com forte afinidade emocional por emoção — o modelo deve priorizá-las.
    # Escolhidas por ressonância temática direta, não por popularidade no corpus.
    _EDITORIAL_PRIMARY_SCRIPTURES = {
        'ansioso': [
            'Mateus 6:25-34',
            'Salmo 131',
            'Mateus 11:28-30',
            'João 14:1-3',
            'Salmo 94:18-19',
            'Lucas 12:22-26',
            'Provérbios 3:5-6',
            'Salmo 55:22',
        ],
        'medo': [
            'Salmo 27:1-4',
            'Isaías 41:10',
            'Marcos 4:35-41',
            'Salmo 56:3-4',
            'Josué 1:9',
            '2 Timóteo 1:7',
            'João 16:33',
            'Salmo 46:1-3',
        ],
        'triste': [
            'Salmo 34:18',
            'Salmo 42:5-11',
            'João 11:33-35',
            'Mateus 5:4',
            'Salmo 30:5',
            'Isaías 53:3',
            'Salmo 147:3',
            'Apocalipse 21:4',
        ],
        'sozinho': [
            'Salmo 139:7-12',
            'Hebreus 13:5',
            'Isaías 43:2-3',
            'João 16:32',
            'Deuteronômio 31:8',
            'Salmo 68:6',
            'Zacarias 2:5',
        ],
        'desmotivado': [
            'Isaías 40:28-31',
            'Gálatas 6:9',
            'Neemias 8:10',
            'Salmo 73:26',
            'Salmo 27:13-14',
            '1 Reis 19:4-8',
            'Romanos 5:3-5',
        ],
        'desesperançoso': [
            'Lamentações 3:21-23',
            'Romanos 8:24-25',
            'Salmo 42:5-11',
            'Salmo 130',
            'Romanos 5:3-5',
            'Hebreus 11:1',
            'Isaías 40:31',
            'Jeremias 29:11',
        ],
        'corajoso-mas-incerto': [
            'Josué 1:9',
            'Isaías 41:10',
            '2 Timóteo 1:7',
        ],
        'chamado-mas-hesitante': [
            'Êxodo 3:11-12',
            'Jeremias 1:6-8',
            'Lucas 5:10-11',
        ],
        'tentado': [
            '1 Coríntios 10:13',
            'Tiago 4:7',
            'Hebreus 4:15-16',
        ],
        'em-conflito-com-alguem': [
            'Colossenses 3:13',
            'Mateus 5:23-24',
            'Romanos 12:18',
        ],
        'grato-mas-disperso': [
            '1 Tessalonicenses 5:16-18',
            'Salmo 103:2',
            'Lucas 17:15-16',
        ],
        'disciplinado-mas-frio': [
            'Apocalipse 2:4-5',
            'Isaías 29:13',
            'João 15:4-5',
        ],
    }

    # Passagens secundárias — aceitáveis mas com menor prioridade.
    # Tendem a aparecer em múltiplas emoções; usadas só se as primárias estiverem esgotadas.
    _EDITORIAL_SECONDARY_SCRIPTURES = {
        'ansioso':        ['1 Pedro 5:7', 'Isaías 26:3', 'Salmo 46:10', 'Romanos 8:28'],
        'medo':           ['Salmo 23', 'Romanos 8:38-39', '1 João 4:18', 'Isaías 26:3'],
        'triste':         ['Salmo 23', 'Romanos 8:28', 'Isaías 40:28-31', '2 Coríntios 4:17'],
        'sozinho':        ['Salmo 23', 'Romanos 8:38-39', 'João 15:15', 'Jeremias 31:3'],
        'desmotivado':    ['Salmo 34:18', 'Jeremias 29:11', 'Salmo 138:3', 'Mateus 11:28-30'],
        'desesperançoso': ['Salmo 23', 'Romanos 8:28', 'Apocalipse 21:4', 'João 14:1-3'],
        'corajoso-mas-incerto': ['Salmo 27:1', '1 Coríntios 16:13', 'Hebreus 13:6'],
        'chamado-mas-hesitante': ['Gênesis 12:1', 'Isaías 6:8', 'Mateus 4:19-20'],
        'tentado': ['Mateus 4:1-11', 'Gálatas 5:16', '2 Pedro 2:9'],
        'em-conflito-com-alguem': ['Efésios 4:31-32', 'Mateus 18:21-22', 'Provérbios 15:1'],
        'grato-mas-disperso': ['Colossenses 3:15-17', 'Salmo 100:4', 'Tiago 1:17'],
        'disciplinado-mas-frio': ['Oséias 6:6', 'Mateus 15:8', 'Salmo 51:10-12'],
    }

    # Categorias de abertura para variar a textura do início da reflexão.
    # Cada entrada: (chave, instrução para o modelo).
    _OPENING_STYLE_CATEGORIES = [
        (
            'imagem_fisica',
            'Comece com uma imagem física e concreta — algo que se vê, toca ou sente no corpo. '
            'Ex: "As mãos não param de se mexer. O estômago fecha antes mesmo de entender por quê."',
        ),
        (
            'observacao_cotidiana',
            'Comece com uma observação do cotidiano ordinário — algo que qualquer um reconheceria. '
            'Ex: "Às vezes a manhã começa pesada antes mesmo de saber por quê."',
        ),
        (
            'frase_curta',
            'Comece com uma frase única e direta, máximo 8 palavras, sem ornamento. '
            'Ex: "Tem dias em que tudo parece demais." ou "O pensamento volta sozinho à noite."',
        ),
        (
            'sensacao_corporal',
            'Comece com uma sensação corporal específica ligada à emoção. '
            'Ex: "É um peso no peito que não se explica. Não é dor exata — é pressão que não passa."',
        ),
        (
            'cena_humana',
            'Comece com uma cena humana breve e reconhecível — um momento específico de vida. '
            'Ex: "Você estava tentando dormir e não conseguia. Três da manhã, o pensamento voltou."',
        ),
        (
            'descricao_concreta',
            'Comece com uma descrição concreta de um estado interno, sem nomeá-lo diretamente. '
            'Ex: "A lista de pendências cresceu mais uma vez. O prazo é amanhã. O corpo não quer saber disso."',
        ),
    ]

    @staticmethod
    def _pick_opening_style() -> tuple:
        """Seleciona aleatoriamente uma categoria de abertura para variar a textura das reflexões."""
        import random
        return random.choice(AnthropicAIService._OPENING_STYLE_CATEGORIES)

    def editorial_generate_devotional(
        self,
        emotion_name: str,
        tone_or_direction: str = None,
        excluded_passages: list = None,
        excluded_themes: list = None,
        excluded_titles: list = None,
        semantic_cooldown_words: list = None,
        ai_request_id: int = None,
    ) -> Dict[str, Any]:
        system_prompt = self._get_editorial_constitution()
        # Normalização robusta do nome para o padrão de slugs com hifens e sem acentos
        emotion_key = emotion_name.lower().strip()
        emotion_key = emotion_key.replace(",", "").replace(".", "").replace("ç", "c").replace("ã", "a").replace("é", "e").replace("í", "i").replace("ó", "o")
        emotion_key = emotion_key.replace(" ", "-").replace("_", "-")

        # 1. Blacklist fixa — aplicada antes das exclusions dinâmicas
        static_blacklist = self._EDITORIAL_PASSAGE_BLACKLIST.get(emotion_key, [])
        dynamic_excluded = list(excluded_passages or [])
        # Merge: blacklist primeiro, sem duplicações
        all_excluded = list(static_blacklist) + [p for p in dynamic_excluded if p not in static_blacklist]

        # 2. Passagens preferenciais disponíveis — filtradas das proibidas
        excluded_set = set(all_excluded)
        available_primary = [p for p in self._EDITORIAL_PRIMARY_SCRIPTURES.get(emotion_key, []) if p not in excluded_set]
        available_secondary = [p for p in self._EDITORIAL_SECONDARY_SCRIPTURES.get(emotion_key, []) if p not in excluded_set]

        # 3. Ângulos humanos por emoção
        angles = self._EDITORIAL_EMOTION_ANGLES.get(emotion_key, [])

        # 4. Estilo de abertura — selecionado aleatoriamente para variar a textura
        style_key, style_instruction = self._pick_opening_style()
        logger.info(
            "[CAPIO OPENING STYLE AUDIT] Emoção '%s' — estilo de abertura selecionado: '%s'",
            emotion_name, style_key
        )

        # Construção do prompt
        prompt = f"Emoção: '{emotion_name}'.\n"
        if tone_or_direction:
            prompt += f"Direção do Editor: '{tone_or_direction}'.\n"

        if all_excluded:
            prompt += "\n[PROIBIDO] PASSAGENS ABSOLUTAMENTE PROIBIDAS — nunca use nenhuma delas:\n"
            prompt += "".join(f"  - {p}\n" for p in all_excluded)

        if excluded_themes:
            prompt += "\n[PROIBIDO] TEMAS PROIBIDOS (já usados):\n"
            prompt += "".join(f"  - {t}\n" for t in excluded_themes)

        if excluded_titles:
            prompt += "\n[PROIBIDO] TITULOS PROIBIDOS:\n"
            prompt += "".join(f"  - {ti}\n" for ti in excluded_titles)

        if semantic_cooldown_words:
            prompt += "\n[RESFRIAMENTO] Estas palavras saturaram os últimos devocionais. Evite-as:\n"
            prompt += "".join(f"  - {w}\n" for w in semantic_cooldown_words)

        if available_primary:
            prompt += f"\n[PREFERENCIAL] Passagens com afinidade emocional para '{emotion_name}' — escolha UMA com prioridade:\n"
            prompt += "".join(f"  + {p}\n" for p in available_primary)

        if available_secondary:
            secondary_label = "use apenas se todas as preferenciais estiverem esgotadas" if available_primary else "use como preferenciais"
            prompt += f"\n[SECUNDARIO] Passagens alternativas ({secondary_label}):\n"
            prompt += "".join(f"  + {p}\n" for p in available_secondary)

        if angles:
            prompt += f"\n[ANGULOS] Experiências humanas para '{emotion_name}' — escolha UMA e construa ao redor dela:\n"
            prompt += "".join(f"  * {a}\n" for a in angles)

        prompt += (
            f"\n[ABERTURA] Estilo obrigatorio para iniciar a reflexao:\n{style_instruction}\n"
            "\n[COMPOSICAO]\n"
            "PONTO DE PARTIDA: A reflexão começa numa experiência humana concreta e reconhecível. "
            "O leitor se reconhece antes de qualquer elaboração teológica.\n"
            "IMAGEM COTIDIANA: Inclua uma imagem discreta do cotidiano (madrugada, janela, respiração, mãos, cama, passos).\n"
            "VOZ: De alguém que atravessou esta experiência, não de narrador espiritual abstrato.\n"
            "PROFUNDIDADE: Vem da verdade emocional específica, não da densidade verbal.\n"
            "\nRetorne UM objeto JSON com os seguintes campos (todos em português):\n"
            "- 'title': Título sóbrio e específico. Humano, não poético demais.\n"
            "- 'scripture_reference': Use preferencialmente as passagens [PREFERENCIAL]. "
            "Nunca use nenhuma da lista [PROIBIDO].\n"
            "- 'scripture_text': Texto exato da passagem.\n"
            "- 'reflection': Reflection. CONDUZ. Responde a: 'O que Deus revelou nesta passagem?'. Max 900 caracteres. Use o estilo de abertura [ABERTURA]. Proibido começar com 'Ha um' ou 'Existe um'. Comeca no chao humano, encontra a Palavra, deixa espaco para contemplacao.\n"
            "- 'practical_application': Gesto humano pequeno e concreto. Não conselho abstrato.\n"
            "- 'guiding_question': Pergunta íntima nascida desta emoção específica. Sem respostas embutidas.\n"
            "- 'prayer': Oracao honesta nascida desta experiência específica. Curta. Sem exclamaçoes.\n"
            "- 'main_truth': Fio da Palavra. ANCORA. Responde a: 'Qual é a verdade que sustenta todo este texto?'. Uma única verdade bíblica sem a qual este devocional deixaria de existir. Simples, bíblica, memorável. NÃO É RESUMO nem conclusão.\n"
            "- 'daily_companion': Palavra Continua. ACOMPANHA. Responde a: 'O que permanecerá acompanhando o leitor hoje?'. Caminha junto com o leitor às 15h da tarde. Sem dar ordens, sem aconselhar, sem mandar (sem imperativos!).\n"
            "- 'share_quote': Share Quote. PERMANECE. Não é gerado, é DESCOBERTO. Responde a: 'Qual frase faria alguém parar a leitura e pensar: preciso enviar isso para alguém que amo?'. REGRA DO LÁPIS ESPONTÂNEO: A frase que um leitor destacaria espontaneamente a lápis. Responda internamente: 'Essa frase existiria mesmo se ninguém fosse compartilhá-la?'. Max 15 palavras. PROIBIDO: paralelismo, frases espelhadas, slogans. Sem exclamaçoes (!).\n"
            "- 'emotional_theme': Max 5 palavras. Subtema humano direto. Sem travessao. Sem descricao adicional.\n\n"
            "AUDITORIA ANTI-REDUNDÂNCIA E COERÊNCIA INVISÍVEL:\n"
            "Reflection -> Fio da Palavra -> Palavra Continua -> Share Quote formam uma única jornada: cada um conduz um passo adiante, nunca resume o anterior, nunca antecipa o próximo.\n"
            "Se remover a Reflection e os outros campos continuarem fazendo sentido sozinho, estão grandes demais. Se remover o Share Quote e o texto não perder nada, está fraco. Se o Daily Companion repetir o Main Truth, reescreva.\n"
            "AUDITORIA FINAL: 'Este texto parece escrito por alguém que deseja impressionar ou por alguém que deseja acompanhar?' Se houver performance literária, reescreva. A beleza deve servir à Palavra.\n"
            "RESTRICOES FINAIS: Sem imperativos. Sem exclamaçoes (!). JSON valido apenas."
        )

        return self._call_claude(
            prompt, system_prompt, 0.75,
            self.mock_fallback.editorial_generate_devotional,
            {"emotion_name": emotion_name, "tone_or_direction": tone_or_direction},
            expected_keys=['title', 'scripture_reference', 'scripture_text', 'reflection', 'prayer', 'share_quote', 'main_truth', 'daily_companion', 'emotional_theme'],
            ai_request_id=ai_request_id,
            endpoint_origin="EDITORIAL_GENERATOR"
        )

    def evaluate_and_refine_editorial(self, content_dict: Dict[str, Any], ai_request_id: int = None) -> Dict[str, Any]:
        system_prompt = (
            "Editor Editorial Único da CAPIO. Concentra clareza, correção gramatical, naturalidade e adesão à Gramática do Silêncio.\n"
            "Diretrizes:\n"
            "1. Clareza acima da Elegância: Sempre preferir a frase que comunica melhor. Teste da Avó. Toda frase deve sobreviver sozinha.\n"
            "2. Abstrações contextuais: Tratar abstrações vagas como diretriz editorial a ser evitada, preferindo palavras concretas da experiência humana.\n"
            "3. Pontuação: Exclamações (!) estritamente proibidas. Interrogações (?) permitidas estritamente para reflexão pastoral genuína.\n"
            "4. A Voz da CAPIO & Teste da Conversa: Escrever para ser compreendido. Pergunta crucial: 'Se este texto fosse lido em voz alta durante um café entre dois amigos, ele soaria natural?' Se parecer ensaio literário ou sermão elaborado, refine.\n"
            "5. O Eco da Palavra & Pergunta Final do Editor Editorial: Valide qual é a única verdade central da reflexão respondendo: 'Quando o leitor fechar a CAPIO daqui a cinco minutos, o que permanecerá com ele?' A resposta deve ser apenas uma ideia simples. Se não conseguir resumir em uma única frase simples, a reflexão perdeu foco e precisa de refinamento.\n"
            "6. Regra da Coerência Invisível e Identidade dos 4 Campos: Reflection -> Fio da Palavra -> Palavra Continua -> Share Quote formam uma única jornada onde cada um conduz o leitor um passo adiante (nunca resume o anterior, nunca antecipa o próximo):\n"
            "   - Reflection: CONDUZ. ('O que Deus revelou?').\n"
            "   - Fio da Palavra (main_truth): ANCORA. Uma única verdade bíblica sem resumo ou conclusão.\n"
            "   - Palavra Continua (daily_companion): ACOMPANHA. Sem dar ordens, sem aconselhar, sem mandar (zero imperativos). Caminha junto às 15h da tarde.\n"
            "   - Share Quote: PERMANECE. Não é gerado, é DESCOBERTO. ('Qual frase faria alguém parar e pensar: preciso enviar isso para alguém que amo?'). REGRA DO LÁPIS ESPONTÂNEO: frase destacada a lápis durante a leitura. Teste: 'Essa frase existiria mesmo se ninguém fosse compartilhá-la?'.\n"
            "   Auditoria Anti-Redundância: Se remover a Reflection e os outros campos fizerem sentido sozinho, estão grandes demais. Se remover o Share Quote e não perder nada, está fraco. Se houver redundância, reprove e reescreva no texto_refinado.\n"
            "7. Auditoria Final Silenciosa: 'Este texto parece escrito por alguém que deseja impressionar ou por alguém que deseja acompanhar?' Se houver performance literária, reescreva. A beleza deve servir à Palavra, nunca competir com ela.\n"
            "8. Score Editorial (0.0 a 10.0) em: 'clareza', 'naturalidade', 'correcao_gramatical', 'aderencia_gramatica_silencio'.\n"
            "Limiar de Excelência: 9.2. Se qualquer critério for < 9.2, houver falta de foco central, repetição funcional ou performance literária, reescreva todo o conteúdo em 'texto_refinado' mantendo as chaves originais. Se todos >= 9.2 e sem redundâncias, texto_refinado = null."
        )
        import json
        prompt = (
            f"Conteúdo em auditoria:\n{json.dumps(content_dict, ensure_ascii=False, indent=2)}\n\n"
            "Retorne APENAS um JSON válido no formato:\n"
            "{\n"
            "  \"scores\": {\"clareza\": X, \"naturalidade\": Y, \"correcao_gramatical\": Z, \"aderencia_gramatica_silencio\": W},\n"
            "  \"aprovado\": true/false,\n"
            "  \"verdade_central_permanente\": \"Uma única frase simples respondendo o que permanecerá com o leitor daqui a cinco minutos\",\n"
            "  \"texto_refinado\": { ... } ou null\n"
            "}\n"
            "Sem markdown."
        )
        res = self._call_claude(
            prompt, system_prompt, 0.4,
            self.mock_fallback.evaluate_and_refine_editorial,
            {"content_dict": content_dict},
            expected_keys=['scores', 'aprovado'],
            ai_request_id=ai_request_id,
            endpoint_origin="EDITORIAL_SCORE"
        )
        return res

    def generate_share_quote(self, reflection: str, ai_request_id: int = None) -> str:
        system_prompt = (
            "Motor Editorial da CAPIO. Formulates ou extrai um Share Quote de até 15 palavras. "
            "Sem autorreferência, sem exclamações. Regra do Lápis Espontâneo."
        )
        prompt = (
            f"Reflexão:\n\"{reflection}\"\n\n"
            "Descubra e extraia o fragmento (share_quote) de até 15 palavras.\n\n"
            "REGRAS (FILOSOFIA DOS SHARE QUOTES):\n"
            "1. NÃO É GERADO, É DESCOBERTO: O Share Quote é a frase que um leitor destacaria espontaneamente com um lápis durante a leitura. Nunca uma frase criada para virar imagem; sempre uma frase encontrada dentro da própria verdade bíblica.\n"
            "2. PENSANDO NO LEITOR: Qual frase faria alguém parar a leitura e pensar: 'preciso enviar isso para alguém que amo'?\n"
            "3. PERGUNTAS DE AUDITORIA SILENCIOSA: Responda internamente antes de gerar: 1. 'Se este devocional fosse publicado em um livro, qual frase um leitor marcaria a lápis?'; 2. 'Essa frase existiria mesmo se ninguém pudesse compartilhá-la nas redes sociais?' Se a resposta for não, reescreva.\n"
            "4. PERMANECE: É a frase que continua ecoando depois que todo o restante desaparece. A beleza deve servir à Palavra, nunca competir com ela.\n"
            "5. SEM IMPERATIVO OU EXCLAMAÇÃO: Proibido 'confie', 'lembre-se', 'busque', 'mude'. Proibido paralelismo artificial ou frases espelhadas. Proibido (!).\n"
            "6. RETORNO: JSON com exclusivamente a chave 'share_quote'. Sem markdown."
        )

        res = self._call_claude(
            prompt, system_prompt, 0.5,
            self.mock_fallback.generate_share_quote,
            {"reflection": reflection},
            expected_keys=['share_quote'],
            ai_request_id=ai_request_id,
            endpoint_origin="SHARE_QUOTE"
        )
        return res.get('share_quote', "Há um descanso real na presença que acompanha o dia.")
