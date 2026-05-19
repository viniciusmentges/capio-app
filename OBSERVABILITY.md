# Guia de Observabilidade e Monitoramento — CAPIO Production

Este documento detalha o sistema de observabilidade, monitoramento de falhas, instrumentação de logs estruturados e estratégias de contingência técnica da **CAPIO** para suportar a escala de produção (1.000+ usuários ativos).

---

## 1. Ativação do Sentry

O monitoramento de erros em tempo real é feito via Sentry de forma condicional e segura. 

### 1.1 Backend (Django)
O Sentry é acionado automaticamente se a variável de ambiente `SENTRY_DSN` estiver presente. O código está blindado contra a ausência da biblioteca local em desenvolvimento (`ImportError`).

1. **Instalação do SDK** (em produção):
   ```bash
   pip install sentry-sdk
   ```
2. **Configuração** (.env):
   ```env
   SENTRY_DSN=https://your-sentry-key@sentry.io/project-id
   ```
   *Nota: A opção `send_default_pii=False` está ativa por padrão para impedir que e-mails de usuários, tokens JWT ou cabeçalhos sensíveis sejam enviados para os servidores externos do Sentry.*

### 1.2 Frontend (React)
Para rastreamento de bugs de renderização no frontend:

1. **Instalação do SDK**:
   ```bash
   npm install @sentry/react
   ```
2. **Configuração** (em `main.jsx` ou `App.jsx`):
   O `ErrorBoundary` global já está preparado para repassar automaticamente as exceções para o Sentry caso `window.Sentry` esteja ativo.
   ```javascript
   import * as Sentry from "@sentry/react";
   
   if (import.meta.env.VITE_SENTRY_DSN) {
     Sentry.init({
       dsn: import.meta.env.VITE_SENTRY_DSN,
       integrations: [Sentry.browserTracingIntegration()],
       tracesSampleRate: 0.1,
     });
   }
   ```

---

## 2. Variáveis de Ambiente de Observabilidade

| Variável | Tipo | Escopo | Descrição |
| :--- | :--- | :--- | :--- |
| `SENTRY_DSN` | String | Backend | URL de ingestão de logs de erro do Sentry. |
| `DEBUG` | Boolean | Backend | Deve ser `False` em produção. Ativa formatação e cap de logs restrito. |
| `USE_REAL_AI` | Boolean | Backend | Se `True`, bate na API Anthropic. Se `False`, usa fallbacks locais (`MockAIService`). |
| `VITE_SENTRY_DSN` | String | Frontend | URL de ingestão de bugs de renderização do Sentry React. |

---

## 3. Logs Estruturados e Eventos Monitorados

Os logs seguem o formato de rastreamento direto e limpo nos canais do servidor.

### 3.1 Logs do Servidor (Django)
* **`[CAPIO AI] Fallback acionado...`** (Warning)
  * *O que significa*: O Claude 3.5 demorou mais que **6.0 segundos** (timeout) ou retornou um erro 5xx. A CAPIO acionou o fallback e serviu um conteúdo de oração seguro pré-cadastrado no banco.
  * *Como ler no console*: `[2026-05-19 00:30:15,120] WARNING in mock: [CAPIO AI] Fallback acionado no fluxo de devocional por emoção para Ansioso.`
* **`Falha ao chamar a API de IA no fluxo...`** (Error)
  * *O que significa*: O pipeline do banco ou rede quebrou gravemente ao registrar a requisição de IA.

### 3.2 Logs do Cliente (Console PWA)
* **`[CAPIO PWA] Conexão física indisponível...`** (Warning)
  * *O que significa*: O usuário perdeu o sinal de internet. O frontend capturou a falha de rede do TanStack Query e buscou o devocional mais recente guardado no IndexedDB.
* **`[CAPIO PWA] Falha de conexão física na API...`** (Warning)
  * *O que significa*: A geração de devocional dinâmico falhou e o app acionou a tela *"Conexão Interrompida"* oferecendo o último registro do IndexedDB.

---

## 4. Endpoint de Health Check

O monitoramento automático de infraestrutura (UptimeRobot, AWS Route53 ou Kubernetes Liveness Probes) deve bater em:

```http
GET /api/health/
```

### Exemplo de Resposta de Sucesso (`200 OK`):
```json
{
  "status": "ok",
  "database": "ok",
  "timestamp": "2026-05-19T03:32:00.123456Z",
  "environment": "production"
}
```

### Exemplo de Resposta de Degradação (`503 Service Unavailable`):
```json
{
  "status": "degraded",
  "database": "error",
  "timestamp": "2026-05-19T03:32:05.999999Z",
  "environment": "production"
}
```

---

## 5. Como Investigar Ocorrências em Produção

### 5.1 Investigando Timeouts de IA (Claude 3.5)
Se os usuários relatarem ver o fallback poético com muita frequência, siga este roteiro de auditoria:
1. Acesse os logs do container Django e filtre por `[CAPIO AI] Fallback acionado`.
2. Verifique o tempo médio de resposta da API externa Anthropic no console.
3. Se os timeouts de 6s forem causados por lentidão global da Anthropic, avalie aumentar a prioridade de pré-geração em lote (Celery) ou ajustar o timeout para 7s.
4. Garanta que a variável `USE_REAL_AI` está de fato ativa (`True`) nas variáveis do cluster.

### 5.2 Investigando Erros de PWA/Offline
Se o usuário relatar tela branca ao desconectar a internet:
1. Abra a aba **Application -> IndexedDB** nos Developer Tools do navegador e confirme se a store `capio_offline_store` existe e possui registros sob as chaves `daily_reflections` ou `devotionals`.
2. Verifique no console se há o erro: `[Storage Offline] Erro ao salvar chave`. Isso pode indicar limite de cota de armazenamento do navegador (raro para JSONs leves).
3. Verifique o painel **Network**. Se as rotas da API retornarem respostas interceptadas com `200 OK` mesmo offline, limpe o cache do Service Worker: um arquivo residual de `sw.js` de versões antigas (v1.2) pode ainda estar registrado no navegador do usuário. O processo de limpeza automática `cleanupOutdatedCaches()` cuidará disso nas visitas seguintes.

---

## 6. Operação Assíncrona: Celery & Redis

A CAPIO possui suporte completo e fundação assíncrona para descarregar o pipeline síncrono HTTP em picos de escala.

### 6.1 Como Rodar o Redis Local (Broker)
O Celery exige o Redis como agente de mensagens (broker). Escolha uma das formas para rodar localmente:

* **Opção 1: Via Docker (Recomendado)**:
  ```bash
  docker run -d -p 6379:6379 redis:alpine
  ```
* **Opção 2: Nativo (Linux/WSL/macOS)**:
  ```bash
  redis-server
  ```
* **Opção 3: Redis no Windows**: Use o WSL ou pacotes nativos para Windows e certifique-se de que está rodando na porta `6379`.

### 6.2 Como Rodar o Worker do Celery Localmente
Com o Redis ativo na porta `6379` e a virtualenv ativa:

```bash
cd backend
celery -A config worker -l info
```
O console mostrará as tarefas registradas da CAPIO:
* `apps.devotional.tasks.generate_devotional_async`
* `apps.bible.tasks.generate_bible_explanation_async`
* `apps.users.tasks.send_silent_push_async`

### 6.3 Como Validar Tarefas Registradas
Você pode testar a integridade das tarefas registradas abrindo um terminal shell interativo do Django (`python manage.py shell`):
```python
from config.celery import app as celery_app
print(celery_app.tasks.keys())
```
Todas as três tarefas principais da CAPIO devem aparecer listadas no dicionário.

### 6.4 Variáveis de Ambiente em Produção
Configure no provedor de nuvem (ex: Render, Heroku ou AWS):

* `CELERY_BROKER_URL=redis://user:password@redis-host:port/0`
* `CELERY_RESULT_BACKEND=redis://user:password@redis-host:port/0`

*Nota: Em ambiente de desenvolvimento, caso não estejam configuradas, o Celery usará o fallback automático local `redis://localhost:6379/0` sem quebrar o servidor Django.*

### 6.5 Comandos de Execução em Produção
* **Servidor Web (Django)**: `gunicorn config.wsgi:application`
* **Processador de background (Celery Worker)**: `celery -A config worker -l info --concurrency=2`

### 6.6 Próximos Passos de Migração Gradual
Quando o time decidir migrar os endpoints síncronos HTTP de IA para o processamento assíncrono definitivo:
1. **Frontend**: Adaptar chamadas para aceitar uma resposta `202 Accepted` com a ID do job.
2. **Polling**: Habilitar o TanStack Query para fazer pooling leve a cada 2s consultando o status do job em `/api/jobs/<job_id>`.
3. **SSE/Websockets (Escala Futura)**: Transitar para Server-Sent Events ou WebSockets para notificar o cliente assim que o Celery preencher o result backend, reduzindo a zero a necessidade de requisições HTTP redundantes.

