# CAPIO Analytics e Observabilidade

## Objetivo

Esta primeira camada implementa tracking discreto de produto, captura de erros e logs estruturados sem alterar a experiencia visual da CAPIO.

## Frontend

PostHog foi centralizado em:

- `frontend/src/analytics/events.js`
- `frontend/src/analytics/posthogClient.js`
- `frontend/src/analytics/AnalyticsProvider.jsx`
- `frontend/src/hooks/useAnalytics.js`

Eventos iniciais:

- `user_registered`
- `user_logged_in`
- `daily_reflection_opened`
- `devotional_started`
- `emotion_selected`
- `devotional_completed`
- `bible_explanation_requested`
- `share_clicked`
- `share_image_generated`
- `pwa_install_prompt_shown`
- `pwa_installed`
- `offline_content_viewed`

O helper vira no-op quando `VITE_POSTHOG_KEY` nao existe. Ele captura erros internos no console e nao bloqueia fluxos offline, PWA ou mobile.

## Sentry

Sentry frontend foi centralizado em `frontend/src/observability/sentry.js` e ativado no `main.jsx`.

Capturas implementadas:

- `ErrorBoundary` React.
- falhas de refresh JWT.
- falhas de armazenamento offline/localForage em fluxos criticos.
- falhas de IA vistas pelo frontend nos fluxos de devocional e explicacao biblica.
- falhas de compartilhamento e geracao de imagem.
- falhas de update de service worker.

No backend, Sentry e configurado por `SENTRY_DSN` em `backend/config/settings/base.py`, com `send_default_pii=False`.

## Backend

Logs estruturados foram centralizados em `backend/services/observability.py`.

Eventos emitidos:

- `ai_request_started`
- `ai_request_success`
- `ai_request_failed`
- `ai_fallback_used`
- `cache_hit`
- `cache_miss`
- `devotional_generated`
- `devotional_served_from_cache`
- `reflection_served_from_cache`
- `bible_explanation_served_from_cache`

Esses eventos saem como JSON pelo logger `services.metrics`, prontos para agregacao em stdout, Sentry logs, Render, Fly, Datadog, Grafana Loki ou outro coletor.

## Variaveis

Frontend:

- `VITE_POSTHOG_KEY`
- `VITE_POSTHOG_HOST`
- `VITE_SENTRY_DSN`
- `VITE_SENTRY_TRACES_SAMPLE_RATE`
- `VITE_APP_VERSION`

Backend:

- `SENTRY_DSN`
- `SENTRY_ENVIRONMENT`

## Como Medir

DAU:
conte usuarios distintos com qualquer evento contemplativo do dia, principalmente `daily_reflection_opened`, `devotional_started` ou `bible_explanation_requested`.

Retencao:
crie cohorts por `user_registered` e acompanhe retorno em D1, D7 e D30 usando `daily_reflection_opened` como evento principal de retorno.

Retorno diario:
meça usuarios que disparam `daily_reflection_opened` em dias consecutivos.

Instalacao PWA:
compare `pwa_install_prompt_shown` com `pwa_installed`.

Compartilhamento:
use `share_clicked` para intencao e `share_image_generated` para material compartilhavel gerado.

Emocoes:
agregue `emotion_selected` por `emotion_slug` e compare com `devotional_completed` para ver queda entre escolha e leitura entregue.

Uso de IA:
no backend, acompanhe `ai_request_started`, `ai_request_success`, `ai_request_failed`, `ai_fallback_used`, `cache_hit` e `cache_miss`. A saude do sistema melhora quando cache hit sobe sem reduzir frescor editorial.

## Proximos Passos

- Criar dashboard PostHog com DAU, retorno diario, PWA install funnel, emocoes mais usadas e share funnel.
- Enviar release real para `VITE_APP_VERSION` e Sentry backend.
- Opcional: adicionar dashboard operacional de custo por `estimated_cost_usd`, tokens e latencia dos logs de IA.
- Opcional: adicionar testes unitarios para garantir que eventos nao lancem excecao quando PostHog/Sentry nao estao configurados.
