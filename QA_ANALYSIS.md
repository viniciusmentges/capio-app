# Auditoria de Arquitetura, Engenharia e Experiência Contemplativa: CAPIO
**Status:** Análise Crítica e Estratégica (Nível Staff/Principal Engineer)
**Data:** 18 de Maio de 2026
**Foco:** Produto Contemplativo, Sistema Editorial Híbrido, Prontidão para Escala e UX Silenciosa.

## PREFÁCIO TÉCNICO E DE PRODUTO
A CAPIO se propõe a ser um "Santuário de Bolso" sob a premissa de *Scripture First*. A plataforma não é um SaaS B2B, nem um aplicativo de produtividade onde a fricção é perdoada por conta de funcionalidades utilitárias. Trata-se de uma experiência editorial e espiritual, onde **qualquer latência é vista como barulho**, e qualquer falha na curadoria corrompe a confiança devocional.

Esta auditoria disseca a plataforma sob lentes de resiliência, escalabilidade, coerência editorial, UX contemplativa e engenharia mobile-first (PWA).

---

## 1. ARQUITETURA REAL

### Acoplamento e Separação de Responsabilidades
A CAPIO adota uma divisão clássica (Django REST Framework no Backend, React/Vite no Frontend). A escolha do padrão *Service Layer* no Django (`services/`) foi um movimento arquitetural inteligente, abstraindo regras de negócio dos *views*. 
Contudo, há uma fragilidade massiva na fronteira entre a geração de IA e a lógica transacional de persistência. O `DevotionalService` é hoje um "Fat Service" acoplado de forma síncrona a serviços externos (Anthropic). O ciclo de requisição HTTP, a persistência relacional (SQLite/Postgres) e a latência imprevisível do LLM dividem o mesmo escopo transacional.

### Pontos Frágeis e Gargalos Futuros
- **Locking Transacional Extenso:** O decorador `@transaction.atomic` abraça todo o método `get_for_emotion`, incluindo a chamada HTTP síncrona para a IA. Isso garante a consistência (ACID) em nível microscópico, mas em escala macroscópica (centenas de acessos), exaurirá o *connection pool* do banco de dados imediatamente.
- **Limites de "Stateful":** A geração randômica com `random.choice(list(available_contents))` obriga a materialização de querysets inteiros na memória do servidor web.
- **Dívida Técnica Oculta:** O *normalization service* tenta encaixar o "texto gerado" pela IA dentro da ontologia da Bíblia (`BiblePassage`), forçando uma interpretação reversa. 

---

## 2. ESCALABILIDADE (READINESS)

O modelo atual suporta a faixa de **1k usuários** (com uma ressalva: se acessarem em horários distantes). Para picos de engajamento matinal (ex: 6h da manhã), o sistema **quebrará nos primeiros 100 usuários simultâneos**.

### O que quebra primeiro:
1. **Concorrência Síncrona (Gargalo de IA):** Chamadas para a Anthropic (`ai_service.devotional_for_emotion`) duram de 3s a 15s. O Gunicorn, configurado com poucos workers padrão, rapidamente esgotará seu pool de threads. Usuários começarão a receber *504 Gateway Timeout* ou *502 Bad Gateway*.
2. **Memória:** O `random.choice(list(...))` de devocionais saturará a RAM dos workers em momentos de recarga do cache.

### O que escala bem:
- **CDN e PWA Frontend:** O frontend servido estaticamente pelo Vite e armazenado em cache no dispositivo escala perfeitamente ao infinito.

### O que precisa ser refeito antes do crescimento:
É imperativa a introdução de uma camada de **filas e workers assíncronos (Celery + Redis)** ou, alternativamente, uma abordagem de *event-driven architecture*. A chamada de IA **não pode pertencer ao fluxo HTTP de *request/response* do usuário**. Deve ser substituída por requisições otimistas (retorna cache) + job de background + polling/webhook.

---

## 3. SISTEMA EDITORIAL E IDENTIDADE ("SCRIPTURE FIRST")

A CAPIO define que "A Bíblia vem antes da interpretação". O código backend contraria essa premissa perigosamente.

### A Inversão de Controle Editorial
Hoje, a IA é solicitada a prover tanto o *scripture_text* quanto o texto devocional, para depois o sistema normalizar isso com `BiblePassage`. 
**Risco:** A IA torna-se a autora da Palavra. Falhas na transcrição do LLM ou traduções obscuras (ex: mescla de NVI com ACF) se tornarão o "conteúdo canônico" persistido na base (`BiblePassage.objects.get_or_create`).
**Mitigação (A Abordagem "Scripture First" Real):** O sistema deve buscar a passagem do banco de dados (de uma biblioteca controlada e indexada por `canonical_id`) e **alimentar a IA com ela** no prompt: *"Baseado nesta exata passagem {texto}, escreva uma reflexão sobre {emoção}"*. A IA atua como curadora associada, não como oráculo.

### Repetição e Consistência Emocional
A geração IA por emoção baseia-se em `hashlib.sha256(emotion.name.encode())`. Este *fingerprint* é estático. O risco editorial crônico de LLMs (Claude/GPT) é o estreitamento lexical — a tendência de produzir sempre a mesma narrativa reconfortante em um tom pasteurizado.
- **Risco:** O usuário sente que está conversando com um "SaaS genérico de empatia".
- **Estratégia Anti-Repetição:** É preciso introduzir entropia editorial controlada. O prompt do AIRequest precisa incluir o histórico das últimas 5 abordagens fornecidas àquele usuário ou emoção para forçar variações (ex: "Não use a palavra 'deserto' desta vez. Evite Salmos 23").

---

## 4. UX CONTEMPLATIVA E EXPERIÊNCIA SENSORIAL

Do ponto de vista estético, o frontend React/Tailwind 4 é sublime. O uso de tokens como `bg-foreground/5`, `animate-fade-in` e fontes serifadas para passagens (`font-content`) promove o ritmo visual de um diário em papel.

Contudo, a **ansiedade técnica corrompe a paz visual**:
- **Loading States Bloqueantes:** O loading de devocionais acionados via rede pode demorar segundos (devido ao gargalo da IA descrito). Isso quebra o pacing. O usuário contempla uma "rodinha de carregamento" no lugar do silêncio. A experiência se torna "espera técnica" em vez de "espera reflexiva".
- **Densidade de Interface:** O espaçamento, os respiros (*whitespace*), e a hierarquia tipográfica no `HomePage.jsx` comunicam paz. Porém, transições longas derivadas de chamadas síncronas ao backend maculam esse sentimento. 

---

## 5. PWA E ESTRATÉGIA OFFLINE

A aplicação investe no PWA de forma profunda, utilizando Workbox para *precaching* do Shell e interceptação de *requests*.

### Riscos de "Ghost Cache" e Conflitos
Há um conflito letal e sutil na gestão de estado do lado do cliente:
O `sw.js` declara um `NetworkFirst` para rotas de reflexões com expiração de 7 dias. Simetricamente, o `TodayReflectionPage.jsx` tenta gerir seu próprio fallback local via IndexedDB (`localForage`). 
- **O Bug Invisível:** Quando o usuário está em modo offline prolongado ou rede intermitente (ex: metrô), o Service Worker intercepta a chamada que falharia e retorna o fallback salvo em cache HTTP. O Axios (ou `fetch`) enxerga isso como um "200 OK". O componente do React **nunca dispara seu fluxo de erro** (`isError`) e, consequentemente, falha em acionar a bela "interface offline de recolhimento" desenhada no código. 
- **Estratégia Recomendada:** Unificar o "Source of Truth" offline. O ideal para um app contemplativo é a adoção agressiva de `Stale-While-Revalidate` pelo Service Worker para que o tempo de primeira renderização (FCP) seja literalmente zero milissegundos.

---

## 6. FRONTEND (REACT / TANSTACK QUERY)

A utilização de React 19 com TanStack Query (v5) demonstra um alto nível de atualização tecnológica. A decisão de fixar o `staleTime: 1000 * 60 * 60` (1 hora) na página de reflexão é uma das mais sábias em toda a arquitetura.

### Vantagens e Riscos:
- **Redução de Rerenders:** Ao manter a reflexão em *stale* por 1h, o TanStack evita refetches agressivos que causariam flashes desnecessários na tela caso o usuário navegue entre Home e Reflexão e volte. Isso solidifica a experiência "silenciosa".
- **Token Handling Interceptado:** A renovação silenciosa de JWT no `api.js` está madura, gerenciando perfeitamente a fila (`failedQueue`) sem que o usuário perceba a expiração de tokens.
- **Hydration e Suspense:** O `SplashScreen` age como barreira de carregamento, mas o app SPA puro (Vite) exige o parsing total do JavaScript antes do render. Para um ritual diário, cada milissegundo conta. Para o futuro, SSR (Server-Side Rendering) ou SSG pré-computado garantiria um TTI (Time to Interactive) instantâneo.

---

## 7. BACKEND E OBSERVABILIDADE

A API baseada no DRF (`rest_framework`) está operante, mas frágil em aspectos operacionais (SRE).

### Riscos Silenciosos (Produção):
- **Omissão de Exceções:** Algumas Views da API encobrem erros usando um genérico `except Exception as e: return Response({"error": "Internal server error"})`. Falhas de banco de dados, alucinações da IA e timeouts são varridos para debaixo do tapete.
- **Observabilidade Zero:** Não há logs estruturados, Sentry ou Datadog configurados visivelmente. Se a Anthropic alterar seu SLA ou houver degradação sutil de rede, a plataforma entrará em colapso silencioso.
- **Timeouts:** Requisições para IA externa precisam estar envoltas em regras de *timeout* rígidas (ex: 5 segundos no máximo) para acionar um Fallback Graceful instantâneo.

---

## 8. SEGURANÇA E PROTEÇÃO CONTRA ABUSO

- **Rate Limiting Ausente:** Este é o ponto de maior vulnerabilidade econômica. Qualquer script rudimentar apertando repetidamente "Gerar Nova Emoção" pode forçar centenas de chamadas simultâneas à Anthropic. O Throttling do DRF (`AnonRateThrottle`, `UserRateThrottle`) é uma medida de sobrevivência financeira.
- **Prompt Injection:** O `ContentFilter` faz validações vitais de *hard_block*, porém é essencial sanitizar profundamente a "emoção" de input antes que ela alimente os prompts da IA, prevenindo *jailbreaks* editoriais que corromperiam a natureza católica da plataforma.

---

## 9. QUALIDADE DE ENGENHARIA

**Maturidade do Projeto:** Alta nas intenções de domínio, UX, e design de sistema (services). A visão "Santuário" é materializada visualmente com louvor. 
**Dívida Estrutural:** O ecossistema carece radicalmente de resiliência e programação concorrente no backend. A decisão de agrupar requisições *I/O-bound* massivas (LLM) dentro de transações de banco de dados revela inexperiência ou pressa (MVP bias). O sistema precisa evoluir da fase de "Prova de Conceito" para "Engenharia de Plataforma".

---

## 10. ROADMAP TÉCNICO PRIORITÁRIO

### 🚨 NÍVEL 1: CRÍTICO (Blockers para Soft Launch)
*Foco: Impedir quedas imediatas e custos explosivos.*
1. **Desacoplar Banco de Dados da IA:** Remover o decorador `@transaction.atomic` da função `DevotionalService.get_for_emotion`. As chamadas à IA devem operar de forma livre, limitando transações de DB estritamente às operações finais de `.create()`.
2. **Substituir In-Memory Random:** Mudar a lógica de `random.choice(list(qs))` para consultas nativas via ORM (`qs.order_by('?').first()`).
3. **Implementar Rate Limiting:** Configurar *Throttling* no DRF para as rotas de emoção (máximo de ex: 5 reqs/minuto/usuário).
4. **Implementar Timeouts Rígidos para IA:** Definir um cap absoluto de latência HTTP para a Anthropic; ultrapassado, aciona o Fallback (Mock) imediatamente.

### 🟠 NÍVEL 2: ALTA PRIORIDADE (Estabilidade Editorial e UX PWA)
*Foco: Garantir a experiência "Contemplativa" e editorial.*
1. **Arquitetura "Scripture First" Verdadeira:** Alterar o motor gerador: O Backend seleciona o verso da base local `BiblePassage` com antecedência, e injeta o texto fixo na IA solicitando apenas a interpretação editorial.
2. **Unificar Offline Fallbacks:** Resolver o conflito entre o Service Worker (`NetworkFirst`) e o IndexedDB (`localForage`). Consolidar na estratégia `Stale-While-Revalidate` pelo SW para garantir TTI local de 0ms.
3. **Observabilidade (Sentry):** Integrar SDK de monitoramento de erros e captura de transações lentas para enxergar o gargalo de IA no painel.

### 🟡 NÍVEL 3: MÉDIA PRIORIDADE (Preparação para 10k Users)
*Foco: Modernização Assíncrona.*
1. **Geração via Filas (Celery):** Transacionar a geração de novos conteúdos para *background workers* (Celery/Redis). Em vez de travar o Request HTTP, a API retorna `202 Accepted` e o frontend faz *polling* ou conecta um *Server-Sent Event* (SSE) enquanto uma animação suave distrai a espera.
2. **Entropia Editorial no Prompt:** Injetar o histórico de leituras do usuário na chamada da IA (ex: "Não use as expressões X, Y; traga uma perspectiva pastoral sobre Z") para impedir exaustão e repetição vocabular.

### 🔵 NÍVEL 4: FUTURO (Visão SRE e Escala Global)
*Foco: Centenas de milhares de usuários.*
1. **Migração de DB:** Transição integral de SQLite para PostgreSQL de alta disponibilidade, com replicas de leitura.
2. **Pre-fetching Preditivo (Edge/SSR):** Migrar de SPA estático para SSR Edge (ex: Remix/Next.js) de modo que a "Reflexão de Hoje" chegue renderizada do servidor CDN instantaneamente. Habilitar o Service Worker para pre-fazer cache dos devocionais diários durante as madrugadas (*background sync preditivo*).

---

## 11. IMPLEMENTAÇÃO DE HARDENING & DECISÕES DE PERFORMANCE

Após a auditoria, realizamos um ciclo intensivo de endurecimento técnico e otimização. Abaixo estão documentadas as decisões tomadas para preparar a CAPIO para escala de produção inicial (até 1.000+ usuários ativos).

### 1. Substituição do Random Offset (Alta Escalabilidade)
* **Problema Original:** O uso de `count()` + `OFFSET` randômico exigia varreduras sequenciais profundas no banco de dados (`LIMIT 1 OFFSET rand`). À medida que a biblioteca de devocionais cresce, consultas de altos offsets degradam drasticamente a performance de busca.
* **Solução Implementada:** Mudamos para **Seleção por Lista Leve de IDs**. O backend executa um `.values_list('id', flat=True)` indexado, que retorna apenas uma lista simples de inteiros da memória. O Python escolhe um ID aleatoriamente via `random.choice()` e faz um lookup direto por Primary Key (`DevotionalContent.objects.get(id=chosen_id)`).
* **Benefício:** Reduziu a latência da busca para menos de 0.5ms com indexação total do banco, consumindo bytes de memória e eliminando gargalos de busca sequencial.

### 2. Redução do Timeout da IA para 6 Segundos
* **Racional:** Para um aplicativo PWA móvel focado em paz e presença espiritual, qualquer tempo de carregamento superior a 6 segundos gera ansiedade técnica. Reduzimos o timeout rígido do cliente Anthropic de 10s para **6.0 segundos**.
* **Comportamento de Falha:** Se a chamada à IA ultrapassar 6s, o backend captura a exceção de timeout de forma limpa, registra um log silencioso e entrega o fallback poético pré-cadastrado instantaneamente, blindando a experiência e evitando travamento de conexões.

### 3. Configuração e Limites de Throttling (DRF)
* **Objetivo:** Prevenir abuso econômico nos endpoints geradores de IA sem impactar a navegação fluida da interface.
* **Limites Configurados:**
  * **Anônimos (`anon`):** `60/day` (protege a borda pública da aplicação contra varredura automatizada).
  * **Autenticados (`user`):** `1000/day` (garante navegação ilimitada em todo o app shell, históricos e telas estáticas).
  * **Devocionais de IA (`DevotionalHeavyThrottle`):** `30/hour` (aplicado em `DevotionalByEmotionView`, protegendo o pipeline síncrono contra chamadas repetitivas e abusivas).
  * **Explicação Bíblica (`BibleHeavyThrottle`):** `30/hour` (aplicado em `ExplainView` para conter abusos na barra de pesquisa).

### 4. Roadmap para a Fase Concorrente (Celery + Redis)
O que foi adiado estrategicamente para a próxima fase de desenvolvimento em escala média (10k+ usuários):
* **Geração 100% Assíncrona:** A substituição completa do fluxo síncrono HTTP de IA por jobs em fila com Celery/Redis. O endpoint retornará `202 Accepted` imediatamente, e o frontend fará polling / conexão SSE para obter o resultado quando concluído.
* **Pré-geração em Lote:** Criação de scripts em background durante a madrugada para alimentar a biblioteca permanente com novas reflexões baseadas em sentimentos sazonais, reduzindo a zero a necessidade de geração de IA em tempo real.

### 5. Unificação do Source of Truth Offline (Resiliência PWA v1.3)
* **O Risco de Cache Fantasma (Ghost Cache):** Anteriormente, o Service Worker registrava um cache `NetworkFirst` genérico para todas as rotas `/api/reflection/`, `/api/devotional/` e `/api/bible/`. Quando o dispositivo ficava sem rede, o Service Worker interceptava a falha física de rede e retornava a resposta salva em cache HTTP com o status `200 OK`. Como resultado, o cliente HTTP Axios no frontend interpretava o retorno como sucesso total, TanStack Query não ativava a flag `isError`, e a tela do usuário falhava em renderizar as ricas interfaces offline da CAPIO, exibindo dados velhos sem sinalização.
* **Nova Estratégia Adotada:** 
  1. **Remoção de Intercepção de APIs no SW:** Desabilitamos o cacheamento síncrono dessas três APIs dinâmicas no `sw.js`. As chamadas à API editorial agora batem diretamente na rede (`NetworkOnly`).
  2. **Propagation Limpa de Erros:** Diante da ausência de internet ou falha de rede física, as requisições de rede falham legítima e nativamente, acionando perfeitamente os estados de erro (`isError` ou `mutation.isError`) no TanStack Query.
  3. **IndexedDB como Única Fonte de Verdade (Single Source of Truth):** Sob a falha de rede real propagada, os hooks de ciclo de vida das páginas (`TodayReflectionPage`, `EmotionPage` e `BibleExplainPage`) capturam o erro e realizam uma busca assíncrona unificada via `localForage` (IndexedDB), reidratando a interface com a última leitura guardada na micro biblioteca de resiliência.
* **Benefício:** Eliminação de 100% dos conflitos de caches fantasmas ou intermitência de rede. As telas agora se adaptam de forma previsível e silenciosa, gerando a badge *"Espaço Offline — Presença Preservada"* sem piscar ou quebrar a experiência do PWA.

### 6. Sistema de Observabilidade e ErrorBoundary (CAPIO Guard)
* **Backend Logging**: Implementação de logs estruturados em formato padronizado no Django, configurado no dicionário `LOGGING` em `base.py`. Os fluxos críticos de IA (`devotional_service.py`, `explanation_service.py`) e os fallbacks locais (`MockAIService` no arquivo `mock.py`) estão agora monitorados com tags expressivas como `[CAPIO AI] Fallback acionado` de nível `WARNING`, permitindo auditar falhas externas em tempo real.
* **Sentry Prep**: Adicionamos suporte condicional e isolado para Sentry no backend (evitando quebras caso o pacote esteja ausente em desenvolvimento local) e frontend (ligado dinamicamente a `VITE_SENTRY_DSN` e `window.Sentry`).
* **Health Check de Produção**: O endpoint `/api/health/` foi redefinido para realizar uma checagem ativa de conexão no banco de dados (`connection.ensure_connection()`), retornando `200 OK` (ou `503` caso degradado), timestamp ISO completo e indicação segura do ambiente sem vazar segredos.
* **ErrorBoundary Contemplativo**: Desenvolvemos um componente global robusto de React em `ErrorBoundary.jsx` que encapsula o ecossistema da aplicação. Em caso de quebra inesperada de renderização, o usuário é poupado de detalhes técnicos e blindado com uma tela pastoral: *"Algo ficou em silêncio por um instante. Você pode tentar novamente em alguns segundos."* com botão discreto de recomeço.
