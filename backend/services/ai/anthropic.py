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
            "9. FORMATO: Responda APENAS em JSON válido, sem texto markdown em volta."
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
            "7. TOM SÓBRIO: Pastoral, silencioso. Sem triunfalismo, coaching ou efeito emocional calculado.\n"
            "8. SEM IMPERATIVOS: Proibido 'Faça', 'Mude', 'Confie'. Use convite ('Há um espaço para...').\n"
            "9. ANTI-ABSTRAÇÃO: Profundidade vem da verdade emocional, não da complexidade verbal. Proibido frases artificialmente profundas.\n"
            "10. BLACKLIST: Proibido 'Jornada', 'Vitória', 'Benção', 'Sucesso', 'Melhor versão'.\n"
            "11. DIVERSIDADE: Cada devocional abre uma porta diferente na mesma emoção.\n"
            "12. FORMATO: Responda APENAS em JSON válido, sem markdown."
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
    }

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

        emotion_key = emotion_name.lower().strip()
        angles = self._EDITORIAL_EMOTION_ANGLES.get(emotion_key, [])

        prompt = f"Emoção: '{emotion_name}'.\n"
        if tone_or_direction:
            prompt += f"Direção do Editor: '{tone_or_direction}'.\n"

        if excluded_passages:
            prompt += "\n⛔ PASSAGENS PROIBIDAS (já usadas nesta emoção):\n"
            prompt += "".join(f"  - {p}\n" for p in excluded_passages)

        if excluded_themes:
            prompt += "\n⛔ TEMAS PROIBIDOS (já usados):\n"
            prompt += "".join(f"  - {t}\n" for t in excluded_themes)

        if excluded_titles:
            prompt += "\n⛔ TÍTULOS PROIBIDOS:\n"
            prompt += "".join(f"  - {ti}\n" for ti in excluded_titles)

        if semantic_cooldown_words:
            prompt += "\n🌡 RESFRIAMENTO SEMÂNTICO — estas palavras saturaram os últimos devocionais. Evite-as como âncoras do texto:\n"
            prompt += "".join(f"  - {w}\n" for w in semantic_cooldown_words)

        if angles:
            prompt += f"\nÂNGULOS HUMANOS para '{emotion_name}' — escolha UM e construa o devocional inteiramente ao redor dele:\n"
            prompt += "".join(f"  • {a}\n" for a in angles)

        prompt += (
            "\nINSTRUÇÕES DE COMPOSIÇÃO:\n"
            "PONTO DE PARTIDA: A reflexão começa numa experiência humana concreta e reconhecível. "
            "O leitor se reconhece antes de qualquer elaboração teológica. Não comece por conceitos espirituais.\n"
            "IMAGEM COTIDIANA: Inclua uma imagem discreta do cotidiano (madrugada, janela, respiração, mãos, cama, passos, manhã, corpo).\n"
            "VOZ: Não de narrador espiritual abstrato. De alguém que realmente atravessou esta experiência e encontrou a Palavra no chão dela.\n"
            "PROFUNDIDADE: Vem da verdade emocional específica, não da densidade verbal.\n"
            "\nRetorne UM objeto JSON (todos os campos em português):\n"
            "- 'title': Título breve e sóbrio. Específico e humano, não poético demais.\n"
            "- 'scripture_reference': Passagem bíblica AINDA NÃO UTILIZADA para esta emoção.\n"
            "- 'scripture_text': Texto exato da passagem.\n"
            "- 'reflection': Máx 900 caracteres. Começa no chão humano, encontra a Palavra, deixa espaço. "
            "Deve soar como anotação íntima de quem sobreviveu, não como sermão contemplativo.\n"
            "- 'prayer': Oração honesta nascida desta experiência específica. Curta. Sem exclamações.\n"
            "- 'share_quote': Máx 15 palavras. Como anotação num caderno às 3 da manhã: "
            "menos efeito dramático, mais verdade interior. Não construída para impacto ou compartilhamento.\n"
            "- 'emotional_theme': Subtema humano e específico (ex: 'Noite sem dormir', 'O pensamento que volta').\n\n"
            "RESTRIÇÕES FINAIS: Sem imperativos. Sem exclamações (!). JSON válido apenas."
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
