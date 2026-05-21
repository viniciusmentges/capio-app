# Auditoria de QA, Arquitetura e Prontidão de Produção: CAPIO (devotional_platform)

**Data:** 20 de Maio de 2026  
**Status:** Concluído  
**Responsável:** Gemini CLI (Senior QA & Staff Engineer)

---

## 1. Resumo Executivo

A plataforma **CAPIO** apresenta um amadurecimento técnico notável em sua identidade de produto ("Scripture First") e em sua experiência PWA. A arquitetura atual, baseada em Django (Backend) e React 19 (Frontend), reflete decisões modernas de engenharia, como o uso de **Service Layer** e **TanStack Query v5**. 

Embora o sistema tenha passado por um ciclo recente de "Hardening" (18/05/2026), ainda persistem riscos críticos relacionados à **concorrência síncrona de IA** e à **ausência de processamento assíncrono integrado** no fluxo do usuário final. O PWA é resiliente, mas a infraestrutura backend precisa de ajustes finos em indexação e desacoplamento para suportar picos de escala (> 1.000 usuários simultâneos).

---

## 2. Diagnóstico Geral

| Categoria | Avaliação | Observação |
| :--- | :--- | :--- |
| **Arquitetura** | Sólida | Separação clara de domínios; Service Layer bem implementada. |
| **Escalabilidade** | Risco Médio/Alto | Gargalo síncrono nas chamadas de IA (Claude). |
| **QA / Estabilidade** | Alta | Cobertura de testes de rotação excelente; resiliência PWA v1.3 ativa. |
| **Segurança** | Boa | JWT maduro; Throttling implementado; Content Filtering funcional. |
| **UX Contemplativa** | Excelente | Foco em silêncio, tipografia e ausência de ruído técnico. |
| **IA / Editorial** | Referência | Motor editorial com resfriamento semântico e "Scripture First" real. |

---

## 3. Pontos Fortes

1.  **Filosofia "Scripture First" Real**: Diferente de MVPs genéricos, a CAPIO agora controla as passagens bíblicas via `EMOTION_SCRIPTURES`, alimentando a IA com a Verdade antes da interpretação.
2.  **Resiliência Offline (PWA)**: A transição para `NetworkOnly` nas APIs, propagando erros para o React que aciona o `localForage` (IndexedDB), resolveu o problema de "Ghost Cache".
3.  **Higiene de Tokens (IA)**: O uso de **Prompt Caching** (Anthropic) e telemetria detalhada de custos (`AIRequest`) demonstra maturidade operacional.
4.  **Motor Editorial Sofisticado**: O sistema de `_SEMANTIC_WATCHLIST` e `_EDITORIAL_EMOTION_ANGLES` garante que a IA não se torne repetitiva ou pasteurizada.
5.  **Throttling**: Proteção financeira contra abusos já configurada via DRF Throttling.

---

## 4. Riscos Críticos

### 🚨 [BACKEND] Latência Síncrona Extrema (Blocker de Escala)
O `AnthropicAIService` está configurado com um **timeout de 120 segundos**. Embora necessário para gerações complexas, as chamadas em `DevotionalService.get_for_emotion` são feitas de forma **síncrona** dentro do ciclo Request/Response.
- **Risco**: Se a Anthropic demorar 30s para responder, um worker do Gunicorn fica preso. Com 10 usuários simultâneos gerando conteúdo, o servidor pode esgotar o pool de conexões e parar de responder a todos.
- **Impacto**: *504 Gateway Timeout* generalizado em horários de pico.

### 🚨 [QA] Ausência de Testes E2E (Confiança de Produção)
Não foram encontrados testes de integração de ponta a ponta (Cypress ou Playwright).
- **Risco**: Mudanças no Service Worker ou na lógica de renovação de token podem quebrar a experiência offline sem detecção automática.
- **Impacto**: Regressões silenciosas em fluxos críticos de usuário.

---

## 5. Riscos Altos

### 🟠 [INFRA] Indexação de Tabelas de Histórico
A tabela `UserDevotional` é consultada via `order_by('-accessed_at')` e filtrada por `user`.
- **Risco**: Atualmente não há um índice explícito (`db_index=True`) em `accessed_at`. Com o crescimento da base (ex: 100k leituras), a geração da janela de rotação (`recently_seen_ids`) se tornará lenta.
- **Arquivo**: `backend/apps/devotional/models.py`.

### 🟠 [IA] Inconsistência de "Scripture First" em Diferentes Fluxos
O fluxo de usuário (`get_for_emotion`) usa passagens curadas, mas o fluxo editorial (`editorial_generate_devotional`) permite que a IA selecione passagens.
- **Risco**: Alucinação de referências ou traduções na biblioteca permanente.
- **Impacto**: Comprometimento da integridade teológica da plataforma.

---

## 6. Análise Detalhada

### 8. Análise Backend (Django / DRF)
- **O que brilha**: O uso do padrão Service Layer desacoplado das Views.
- **Dívida Técnica**: O Celery está instalado e configurado, mas as tarefas (`tasks.py`) **não estão integradas** ao fluxo de vida real do usuário. A geração de IA deveria ser um job de background com polling no frontend.
- **Bugs Prováveis**: No `NormalizationService`, o conflito entre "Jo" (João) e "Jó" (Jó) pode levar a exegeses incorretas se o usuário não usar acentuação.

### 9. Análise Frontend (React / Vite)
- **Performance**: O uso de `staleTime: 1h` no TanStack Query é perfeito para a proposta contemplativa.
- **UX Mobile**: A interface é mobile-first e respeita os princípios de silêncio (ausência de exclamações, fontes serifadas).
- **Tratamento de Erros**: O `ErrorBoundary` global protege contra "White Screen of Death".

### 10. Análise PWA / Offline
- **Estratégia**: Robusta. O uso de `cleanupOutdatedCaches()` e `precacheAndRoute()` garante que o App Shell esteja sempre atualizado.
- **Cache**: O cache de fontes (1 ano) e imagens (30 dias) está bem configurado.
- **Melhoria**: Falta um sistema de "Background Sync" para pré-carregar a reflexão do dia seguinte enquanto o usuário ainda tem rede.

### 11. Análise IA / Editorial
- **Prompts**: Estão entre os melhores já vistos para este tipo de aplicação. As "Regras de Ouro" e o "Resfriamento Semântico" são diferenciais de mercado.
- **Custo**: Bem monitorado, mas a troca de Haiku por Sonnet sem aviso pode triplicar o custo operacional.

---

## 12. Escalabilidade (Load Testing Hipotético)

- **100 usuários**: O sistema aguenta, desde que a biblioteca tenha conteúdo pré-gerado (cache hit).
- **1.000 usuários**: Provável falha de concorrência se a IA for acionada simultaneamente por 5% dos usuários (gargalo de workers síncronos).
- **10.000 usuários**: Necessita obrigatoriamente de Celery para geração de IA e migração total para Postgres (se ainda estiver em SQLite).

---

## 13. Bugs Prováveis Encontrados

1.  **Conflito de Normalização**: `Jo 1:1` vs `Jó 1:1` em `normalization.py`.
2.  **Missing Indexes**: `accessed_at` em `UserDevotional` e `input_hash` em `AIRequest`.
3.  **Fase 3 do Fragmento Editorial**: O arquivo `EDITORIAL_FRAGMENT_ARCHITECTURE.md` descreve entidades que **não existem** no código atual (`EditorialFragment`, `UserFavoriteFragment`). O código ainda usa o modelo linear legado.

---

## 14. Dívidas Técnicas

- **Fase de Testes**: Transição de "Scripts de Teste" para um framework de testes automatizados integrado (Pytest).
- **Assincronia**: O Celery está "dormente" (declarado mas não utilizado no fluxo crítico).
- **Logs**: Os logs estão estruturados mas não há indicação de exportação para um agregador (ELK/Sentry).

---

## 15. Recomendações Práticas e Roadmap Priorizado

### 🟢 Agora / Crítico (Pré-Lançamento/Crescimento)
1.  **Desacoplar Fluxo de IA (Celery)**: Integrar `generate_devotional_async` no fluxo. O frontend deve receber um `202 Accepted` e mostrar uma animação de "preparando o silêncio" enquanto faz polling.
2.  **Adicionar Índices de Banco**:
    *   `UserDevotional.accessed_at`
    *   `AIRequest.input_hash`
    *   `DevotionalContent.is_active` e `reviewed_by_human`
3.  **Sanitização de Slugs**: Garantir que o input de `emotion_slug` nas views seja estritamente validado contra o banco para evitar qualquer tentativa de exploração de lógica.

### 🟡 Curto Prazo (Estabilidade)
1.  **Testes E2E**: Implementar 3 fluxos críticos em Playwright (Login -> Leitura -> Offline -> Logout).
2.  **Fallback de IA Global**: Implementar um `Circuit Breaker` que desativa a geração de IA se a Anthropic falhar 3 vezes seguidas, forçando o uso exclusivo da biblioteca por 5 minutos.
3.  **Melhoria na Normalização**: Diferenciar "Jo" de "Jó" de forma mais robusta em `normalization.py`.

### 🟠 Médio Prazo (Escala e Maturidade)
1.  **Entidade EditorialFragment**: Implementar a Fase 3 da arquitetura de fragmentos para permitir múltiplos "Share Quotes" por reflexão.
2.  **Background Sync**: Configurar o Service Worker para buscar a reflexão do dia seguinte (`/api/reflection/today`) automaticamente em background.

### 🔵 Futuro
1.  **SSR / Edge Delivery**: Migrar a página de Reflexão Diária para renderização no Edge para TTI (Time to Interactive) de sub-100ms em qualquer lugar do mundo.

---

## Checklist de Ações Recomendadas

1.  [ ] **[BACKEND]** Remover chamada síncrona da IA no `DevotionalService` e substituir por Celery.
2.  [ ] **[DB]** Adicionar `db_index=True` nos campos `accessed_at`, `input_hash` e flags de status.
3.  [ ] **[QA]** Criar suite de testes E2E para o PWA.
4.  [ ] **[IA]** Unificar lógica de "Scripture First" entre fluxos de usuário e editorial.
5.  [ ] **[PWA]** Validar se o manifest.json e ícones estão 100% compatíveis com iOS (Safari).

---
*Assinado,*  
**Gemini CLI**  
*Senior QA & Staff Engineer*
