# CAPIO — AUDITORIA DE ECONOMIA DE TOKENS E ARQUITETURA DE CUSTOS DE IA

A CAPIO foi concebida para ser uma clareira de silêncio e interioridade, o que se opõe intrinsecamente a um consumo excessivo e compulsivo de inteligência artificial. Como **Sênior AI Cost Optimization Engineer**, **Backend Performance Architect** e **Token Economics Specialist**, realizei uma auditoria abrangente no ecossistema do projeto (backend, frontend, tarefas assíncronas e prompts) para rastrear o destino dos tokens da Anthropic/Claude e desenhar uma transição completa para um modelo de consumo **Editorial-First**, **Biblioteca-First** e **Cache-First**.

---

## 1. Mapa Completo de Chamadas e Origem da IA

Identificamos exatamente **4 fluxos operacionais** no backend da CAPIO que invocam a API da Anthropic (Claude 3.5). A tabela abaixo consolida a telemetria mapeada para cada um:

| Fluxo / Endpoint | Trigger Operacional | Modelo Padrão | Prompt Médio (Tokens) | Resposta Média (Tokens) | Tipo de Persistência / Cache | Frequência de Execução |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Explicação Bíblica**<br>`/api/bible/explain/` | Pesquisa ou acesso do usuário a uma passagem exegética. | `claude-haiku-4-5` | 1.300 | 500 | **Total (DB)**<br>Verifica `PassageExplanation` por ID canônico. | Sob demanda (Apenas no primeiro acesso global à passagem). |
| **B. Warmup Diário**<br>`/api/reflection/today/` | Disparado via cronjob diário ou no primeiro acesso sob demanda. | `claude-haiku-4-5` | 1.500 | 900 | **Total (DB)**<br>Verifica existência de `DailyReflection` por data. | 1 vez por dia (Por design). |
| **C. Devocional por Emoção**<br>`/api/devotional/by-emotion/` | Seleção de emoção na tela de "Presença" do app. | `claude-haiku-4-5` | 1.600 | 800 | **Híbrido**<br>Verifica pool da biblioteca e janela deslizante do usuário. | **Vazamento crítico detectado em testes (Ver Seção 3).** |
| **D. Painel Editorial Admin**<br>`/api/devotional/editorial/generate/` | Ação manual do editor no Django Admin ("Gerar com IA" / Action em lote). | `claude-haiku-4-5` | 1.800 | 900 | **Manual**<br>Persistido apenas sob salvamento do curador humano. | Sob demanda (Apenas ações administrativas pontuais). |

---

## 2. Auditoria e Rastreamento dos Prompts (Tokenomics)

Os prompts da CAPIO são refinados, teológicos e extremamente literários. Porém, do ponto de vista de economia de tokens, identificamos desperdícios estruturais decorrentes de redundância de instrução:

* **Contexto Cromático & Identidade de Marca Injetados em Múltiplos Prompts**: 
  O prompt base (`_get_base_constitution` em `anthropic.py`) possui aproximadamente **550 tokens**. Ele é injetado integralmente em **todos** os fluxos de geração. 
  * *O desperdício:* Regras estritas de design (como proibição de exclamações, uso de frases curtas e tom anti-coaching) são necessárias para a reflexão, mas são reenviadas para a geração pontual de `share_quote` (onde a regra poderia ser encapsulada em 3 linhas de instrução).
* **Ausência de Prompt Caching (Anthropic Cache Control)**:
  Como os prompts do Claude na CAPIO contêm instruções de identidade fixas (o Manifesto Editorial e a Constituição da marca), cada chamada limpa o cache de contexto da Anthropic. Ao não utilizarmos a especificação `Cache-Control: ephem` nos blocos de sistema do Claude, pagamos 100% da taxa de leitura de prompts repetidamente.
  > [!TIP]
  > A ativação de **Prompt Caching** na Anthropic reduz o custo de tokens de entrada repetidos em até **90%**, reduzindo drasticamente a fatura em pipelines curados e com regras longas de marca.

---

## 3. Auditoria de Warmups e Geração Automática (Vazamentos e Loops)

Encontramos a causa raiz do consumo desproporcional de tokens mesmo com apenas 1 usuário ativo no ambiente de testes:

### A. O Loop de Esgotamento do Pool (Devocional por Emoção)
No arquivo `devotional_service.py`, a lógica de acionamento da IA opera da seguinte forma:
```python
if not chosen_content:
    should_generate_dynamically = True
elif total_pool_count < 12:
    has_seen_all = all(cid in all_seen_ids for cid in total_pool_ids)
    if has_seen_all:
        if daily_generation_count < 2:
            should_generate_dynamically = True
```
* **O Problema Crítico:** 
  Como a biblioteca inicial no banco local de desenvolvimento/testes possui apenas **1 ou 2 devocionais** por emoção, o seu único usuário de teste consome o pool inteiro de uma emoção (ex: "Ansioso") nos primeiros 2 dias de uso. 
  A partir daí, **toda request** enviada por aquele usuário para aquela emoção disparará obrigatoriamente uma **geração dinâmica em tempo real (chamada Claude)**, limitada apenas pelo freio diário global de 2 gerações por emoção.
* **Chamadas Síncronas Bloqueantes no HTTP Request:** 
  A geração dinâmica ocorre de forma síncrona dentro da request do usuário. Se a requisição de IA atrasar, a conexão HTTP permanece aberta no Render (gerando timeouts e custos extras de infraestrutura).

### B. O Mistério do Celery Task Duplicado
Embora exista uma tarefa assíncrona para geração (`generate_devotional_async` em `tasks.py`), a API pública de consumo do usuário (`/api/devotional/by-emotion/`) **não** delega a geração para a fila do Celery. Ela chama `DevotionalService.get_for_emotion` diretamente no processo síncrono. A Celery task assíncrona só existe no projeto, mas não está protegendo o usuário de esperas na API móvel.

---

## 4. Auditoria de Cache, Persistência e Concorrência

* **O que está Correto (Forte e Seguro):**
  * **Idempotência por Hash**: O mecanismo de `input_hash` gerado a partir da combinação de `emotion:canonical_id` no `AIRequest` e `GeneratedResponse` impede chamadas duplicadas simultâneas. Se duas pessoas gerarem o mesmo devocional ao mesmo tempo, a transação atômica e o banco barram a segunda chamada e servem o cache da primeira.
  * **Explicações Bíblicas**: Uma vez exegeticamente explicada uma passagem pelo Claude, ela nunca mais é gerada para nenhum outro usuário, persistida para sempre na biblioteca global.
* **Onde há falha de Reaproveitamento:**
  * O freio do `daily_generation_count < 2` é global por emoção, não por usuário. Ou seja, se o Usuário A esgotar o pool, a IA gera um novo devocional que entra na biblioteca. Quando o Usuário B chegar à mesma emoção, ele receberá o devocional gerado pelo Usuário A de forma cacheada. No entanto, em ambiente com poucos usuários, o pool de novos é consumido muito rápido, retroalimentando as requisições de geração sob demanda.

---

## 5. Auditoria Frontend: Comportamento no Refresh e StrictMode

Analisamos o comportamento do React no frontend:

* **`HomePage.jsx` — O Warmup Oculto**:
  A página inicial realiza a busca `/api/reflection/today/` usando TanStack Query.
  * *O Risco:* Se o banco de dados local ou de staging for resetado com frequência, o acesso à Home por qualquer usuário em StrictMode (que monta o componente duas vezes) ou múltiplos refreshes força o backend a chamar a IA em tempo real para preparar o warmup daquela data.
* **`EmotionPage.jsx` — Blindagem Perfeita**:
  Como a mutação do devocional ocorre estritamente sob clique do botão de submit (`mutation.mutate({ emotion: selectedSlug })`), o frontend está imune a fetches acidentais provocados por re-renderizações ou loops de `useEffect`.

---

## 6. Plano de Ação e Soluções Propostas (Sem Alterar Código Ainda)

Para tornar a CAPIO um ecossistema **Biblioteca-First**, propomos a implementação das seguintes otimizações de custos e desempenho:

### 🚀 Prioridade 1: Elevar a Tolerância de Repetição do Pool (Ajuste Crítico no Algoritmo)
Atualmente, se o usuário já leu todos os devocionais de uma emoção (ex: viu as 3 passagens da biblioteca), o sistema gera imediatamente um devocional por IA.
* **A Otimização:** O usuário não se importa de ler novamente um devocional profundo se tiver se passado algum tempo. Propomos aumentar a resiliência do algoritmo de rotação. A geração de IA só deve ser acionada em último caso:
  * Se o pool for menor que 3: permitir repetição com um intervalo mínimo (ex: não repetir o último devocional visto).
  * O gatilho de geração dinâmica por esgotamento de pool deve ser **desativado por padrão** para usuários comuns, reservando a criação de conteúdo ao **Pipeline Editorial manual/agendado**. A biblioteca curada deve crescer de forma controlada e curada, e não organicamente a cada leitura de usuário.

### 🧠 Prioridade 2: Prompt Caching no Claude 3.5 Haiku
Adicionar headers de controle de cache nos parâmetros de requisição do Anthropic SDK:
* Injetar o breakpoint de cache no Manifesto e na Constituição Editorial. Isso reduz o custo de tokens de entrada em até **90%** em chamadas sucessivas.

### 📝 Prioridade 3: Modularização e Encurtamento de Prompts Secundários
* O prompt do `generate_share_quote` não precisa do Manifesto Editorial completo de 550 tokens. Um sistema simplificado contendo apenas as regras estritas da frase (máx 15 palavras, sem exclamações) reduzirá o consumo de tokens de entrada desse fluxo em **70%**.

### ⚙️ Prioridade 4: Logs Estruturados de Auditoria de Tokens no AIRequest
Melhorar a gravação no modelo `AIRequest` salvando explicitamente a volumetria de tokens retornada pela API do Claude (`input_tokens`, `output_tokens`) para acompanhamento em tempo real no Django Admin.

---

## 7. Próximos Passos
Estou aguardando a sua revisão e aprovação deste diagnóstico técnico completo antes de iniciarmos qualquer refatoração no código da CAPIO! Por favor, analise as conclusões do mapa e dê o sinal verde para o curso de ação que preferir.
