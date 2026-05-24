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
            "9. FORMATO: Responda APENAS em JSON válido, sem texto markdown em volta.\n"
            "10. LIBERDADE TEMÁTICA: A CAPIO não é apenas sobre silêncio e repouso. Pode abordar coragem, obediência, chamado, serviço, disciplina, perdão ativo e perseverança prática. O silêncio e a quietude são a forma literária e a postura da escrita, e não o único tema permitido.\n"
            "11. FIDELIDADE E GRAÇA: Quando o estado emocional for ativo ou convocativo, a CAPIO pode chamar o leitor à fidelidade, mas nunca à performance. Pode confrontar, mas nunca esmagar. Pode convidar à obediência, mas sempre a partir da graça."
        )

    def _get_editorial_constitution(self) -> str:
        """Prompt de sistema compacto exclusivo do motor editorial.
        Otimizado para clareza humana, anti-abstração e token economy."""
        return (
            "Motor Editorial da CAPIO. Não é chatbot. Não é narrador espiritual abstrato.\n\n"
            "REGRAS INVIOLÁVEIS:\n"
            "1. SCRIPTURE-FIRST: A Palavra é o centro. Iluminar, nunca substituir.\n"
            "2. HUMANIDADE CONCRETA: O texto nasce de experiência humana real e reconhecível. Nunca de conceito espiritual abstrato.\n"
            "3. CLAREZA PRIORITÁRIA: Compreensível por alguém emocionalmente exausto. Proibido linguagem nebulosa ou etérea.\n"
            "4. SEM AUTORREFERÊNCIA: Proibido 'eu', 'nós', frases auto-referenciais.\n"
            "5. SEM EXCLAMAÇÃO: Proibido (!). Pontos e vírgulas apenas.\n"
            "6. FRASES CURTAS: Máx 15 palavras. Máx 2 adjetivos por parágrafo.\n"
            "7. TOM SÓBRIO: Pastoral, silencioso. Sem triunfalismo, coaching ou efeito emocional calculated.\n"
            "8. SEM IMPERATIVOS: Proibido 'Faça', 'Mude', 'Confie'. Use convite ('Há um espaço para...').\n"
            "9. ANTI-ABSTRAÇÃO: Profundidade vem da verdade emocional, não da complexidade verbal. Proibido frases artificialmente profundas.\n"
            "10. BLACKLIST: Proibido 'Jornada', 'Vitória', 'Benção', 'Sucesso', 'Melhor versão'.\n"
            "11. DIVERSIDADE: Cada devocional abre uma porta diferente na mesma emoção.\n"
            "12. FIDELIDADE E GRAÇA: Quando o estado emocional for ativo ou convocativo, a CAPIO pode chamar o leitor à fidelidade, mas nunca à performance. Pode confrontar, mas nunca esmagar. Pode convidar à obediência, mas sempre a partir da graça.\n"
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

    def devotional_for_emotion(self, emotion_name: str, reference_display: str, scripture_text: str, ai_request_id: int = None) -> Dict[str, Any]:
        system_prompt = self._get_editorial_constitution()
        prompt = (
            f"Emoção: {emotion_name}\n"
            f"Passagem Bíblica: {reference_display}\n"
            f"Texto: \"{scripture_text}\"\n\n"
            "PONTO DE PARTIDA: Comece pela experiência humana concreta desta emoção. "
            "O leitor se reconhece antes de qualquer elaboração teológica. "
            "Inclua uma imagem discreta do cotidiano (respiração, mãos, manhã, corpo, janela).\n"
            "Retorne UM objeto JSON (todos em português):\n"
            "- 'title': Título sóbrio e específico. Humano, não poético demais.\n"
            "- 'reflection': Reflexão de até 800 caracteres. Começa no chão humano, encontra a Palavra, deixa espaço.\n"
            "- 'practical_application': Gesto humano pequeno e concreto. Não conselho abstrato.\n"
            "- 'guiding_question': Pergunta íntima nascida desta emoção específica. Sem respostas embutidas.\n"
            "- 'prayer': Oração honesta e curta. Nascida da experiência, não de fórmula. Sem exclamações."
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
            "Retorne UM objeto JSON com:\n"
            "- 'title': Título contemplativo e específico.\n"
            "- 'scripture_reference': A passagem guia de hoje (nunca repita as listadas no bloco [PROIBIDO] e priorize as recomendadas pelo EIXO TEMÁTICO se possível).\n"
            "- 'scripture_text': O texto da Palavra.\n"
            "- 'reflection_body': Meditação profunda (máx 1000 caracteres). Começa no chão humano, encontra a Palavra, deixa espaço. ATENÇÃO: Não domesticar a reflexão do dia! A reflexão diurna deve preservar toda a força, tensão bíblica, profundidade e confronto saudável (honestidade espiritual, podendo falar de luta, obediência ativa, chamado, tentação, conflito interior e resistência). Não a torne artificialmente calma ou anestesiada.\n"
            "- 'guiding_question': Pergunta para carregar no coração.\n"
            "- 'closing_prayer': Oração curta de encerramento para a noite (Palavra da Noite). Deve conduzir o tema do dia ao silêncio. Calibre-a estritamente para o repouso noturno: evite tensões ou confronto aqui. Deve inspirar confiança silenciosa, repouso, desaceleração, respiração, quietude e entrega de fim de dia no Senhor.\n"
            "- 'share_quote': Um eco ou fragmento de recolhimento noturno (máx 15 palavras) inspirado ou extraído da própria reflexão. Deve soar como uma vela acesa no fim do dia, uma releitura silenciosa que repousa e permanece no silêncio da noite, inspirando quietude e confiança tranquila.\n"
            "- 'emotional_theme': Subtema em até 5 palavras, usado para rastreamento semântico.\n\n"
            "REGRAS ESTRITAS DE RITUAL NOTURNO PARA 'closing_prayer' E 'share_quote':\n"
            "1. DIREÇÃO DA NOITE: A noite não apaga o tema do dia; ela apenas o conduz suavemente ao silêncio, ao repouso e à permanência pacífica no Senhor.\n"
            "2. PROIBIÇÃO DE CONFRONTO E TENSÃO NA NOITE: A oração de encerramento e o share_quote devem focar em paz, descanso espiritual e respiração calma, sem acusações ou pressões.\n\n"
            "REGRAS ESTRITAS DE ARQUITETURA PARA 'share_quote':\n"
            "1. LINGUAGEM DE LIVRO: Use palavras densas, sóbrias e humanas. Não se limite apenas a 'silêncio, presença, espera' — expresse verdade e profundidade.\n"
            "2. PROIBIÇÃO DE AUTOAJUDA/COACHING: Banido imperativos (não use 'lembre-se', 'busque', 'confie', 'mude'). Banido jargões gospel ('Deus vai fazer', 'vitória', 'jornada', 'bênção').\n"
            "3. ZERO PONTUAÇÃO EXCESSIVA: Proibido absolutamente o uso de exclamações (!). Use apenas pontos e vírgulas.\n"
            "4. RITMO E COMPRIMENTO: Curto e memorável sem ser clichê. Máximo de 15 palavras. Frase limpa, sem aspas adicionais dentro da string."
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
                'title', 'scripture_reference', 'scripture_text', 'reflection_body', 
                'guiding_question', 'closing_prayer', 'share_quote', 'emotional_theme'
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
            "\nRetorne UM objeto JSON (todos os campos em português):\n"
            "- 'title': Título sóbrio e específico. Humano, não poético demais.\n"
            "- 'scripture_reference': Use preferencialmente as passagens [PREFERENCIAL]. "
            "Nunca use nenhuma da lista [PROIBIDO].\n"
            "- 'scripture_text': Texto exato da passagem.\n"
            "- 'reflection': Max 900 caracteres. Use o estilo de abertura [ABERTURA]. "
            "Proibido começar com 'Ha um' ou 'Existe um'. "
            "Comeca no chao humano, encontra a Palavra, deixa espaco.\n"
            "- 'prayer': Oracao honesta nascida desta experiência específica. Curta. Sem exclamaçoes.\n"
            "- 'share_quote': Max 15 palavras. Observacao íntima guardada no coracao, nao construída para impacto. "
            "PROIBIDO: paralelismo, estrutura espelhada (A->B / A'->B'), frases criadas para soar memoráveis. "
            "OBRIGATORIO: gramaticalmente correto. Tom interior, nao performático.\n"
            "- 'emotional_theme': Max 5 palavras. Subtema humano direto. Sem travessao. Sem descricao adicional.\n\n"
            "RESTRICOES FINAIS: Sem imperativos. Sem exclamaçoes (!). JSON valido apenas."
        )

        return self._call_claude(
            prompt, system_prompt, 0.75,
            self.mock_fallback.editorial_generate_devotional,
            {"emotion_name": emotion_name, "tone_or_direction": tone_or_direction},
            expected_keys=['title', 'scripture_reference', 'scripture_text', 'reflection', 'prayer', 'share_quote', 'emotional_theme'],
            ai_request_id=ai_request_id,
            endpoint_origin="EDITORIAL_GENERATOR"
        )

    def generate_share_quote(self, reflection: str, ai_request_id: int = None) -> str:
        system_prompt = (
            "Motor Editorial da CAPIO. Extrai um fragmento de até 15 palavras de uma reflexão fornecida. "
            "Sem autorreferência, sem exclamações, sem dramaticidade calculada."
        )
        prompt = (
            f"Reflexão:\n\"{reflection}\"\n\n"
            "Extraia ou formule um fragmento (share_quote) de até 15 palavras.\n\n"
            "REGRAS:\n"
            "1. TOM: Como anotação íntima num caderno às 3 da manhã. Menos efeito, mais verdade interior.\n"
            "2. ANTI-IMPACTO: Não construída para ser compartilhável ou memorável. Construída para ser verdadeira.\n"
            "3. SEM IMPERATIVO: Proibido 'confie', 'lembre-se', 'busque', 'mude'. Sem jargão gospel.\n"
            "4. SEM EXCLAMAÇÃO: Apenas pontos e vírgulas.\n"
            "5. RETORNO: JSON com exclusivamente a chave 'share_quote'. Sem markdown."
        )

        res = self._call_claude(
            prompt, system_prompt, 0.5,
            self.mock_fallback.generate_share_quote,
            {"reflection": reflection},
            expected_keys=['share_quote'],
            ai_request_id=ai_request_id,
            endpoint_origin="SHARE_QUOTE"
        )
        return res.get('share_quote', "Há um peso que não precisa ser carregado sozinho.")
