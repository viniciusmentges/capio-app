# Checklist de Deploy & Auditoria Operacional — CAPIO

Este documento consolida o guia de prontidão operacional e o checklist final para o deploy seguro da **CAPIO** em ambientes de produção real (ex: Render, AWS, Heroku ou similar).

---

## 1. Variáveis de Ambiente Obrigatórias

### 1.1 Backend Django (`.env`)
Estas variáveis devem estar configuradas no painel da sua nuvem (ex: Render Web Service e Celery Worker):

| Variável | Tipo | Exemplo / Valor | Descrição |
| :--- | :--- | :--- | :--- |
| `DEBUG` | Boolean | `False` | **CRÍTICO:** Desativa logs de debug e stack traces para o usuário. |
| `SECRET_KEY` | String | `sua-chave-secreta-longa-e-aleatoria` | Chave criptográfica do Django. |
| `DATABASE_URL` | String | `postgres://user:pass@host:port/dbname` | URL de conexão com o banco PostgreSQL. |
| `ALLOWED_HOSTS` | List | `api.capio.app,capio.app` | Domínios autorizados a acessar o backend. |
| `CORS_ALLOWED_ORIGINS` | List | `https://capio.app` | Domínios frontend permitidos (CORS). |
| `SENTRY_DSN` | String | `https://key@sentry.io/project` | URL de monitoramento de exceções (Opcional). |
| `CELERY_BROKER_URL` | String | `redis://:pass@redis-host:6379/0` | **Obrigatório:** URL do Redis de entrada das tarefas. |
| `CELERY_RESULT_BACKEND` | String | `redis://:pass@redis-host:6379/0` | **Obrigatório:** URL do Redis para salvar resultados. |
| `USE_REAL_AI` | Boolean | `True` | Define o uso do Claude 3.5. Em desenvolvimento, use `False`. |
| `ANTHROPIC_API_KEY` | String | `sk-ant-apiv1-...` | Chave de produção da Anthropic. |

### 1.2 Frontend React (`.env.production`)
Essas variáveis devem ser injetadas durante o processo de build do frontend (Vite):

| Variável | Tipo | Exemplo / Valor | Descrição |
| :--- | :--- | :--- | :--- |
| `VITE_API_URL` | String | `https://api.capio.app` | URL HTTPS absoluta do Django Backend. |
| `VITE_VAPID_PUBLIC_KEY` | String | `B...VAPID_CHAVE_REAL` | Chave pública VAPID do Web Push. |
| `VITE_SENTRY_DSN` | String | `https://key@sentry.io/proj` | Rastreamento de erros no frontend (Opcional). |

---

## 2. Comandos Operacionais

### 2.1 Pipeline de Deploy: Backend
Execute no ambiente do servidor web Django:

1. **Instalação das dependências**:
   ```bash
   pip install -r requirements/base.txt
   ```
2. **Coleta de arquivos estáticos**:
   ```bash
   python manage.py collectstatic --noinput
   ```
3. **Execução de Migrations** (Banco de dados):
   ```bash
   python manage.py migrate --noinput
   ```
4. **Inicialização do Servidor Web** (Gunicorn / WSGI):
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```

### 2.2 Pipeline de Deploy: Celery Worker
Execute no container/ambiente do processador assíncrono (mesmo repositório, mas inicializado como worker):

1. **Inicialização do Worker**:
   ```bash
   celery -A config worker -l info --concurrency=2
   ```

### 2.3 Pipeline de Deploy: Frontend (PWA)
Execute no servidor de assets estáticos (ex: Netlify, Vercel, ou Render Static Site):

1. **Instalação de pacotes**:
   ```bash
   npm ci
   ```
2. **Build de Produção**:
   ```bash
   npm run build
   ```
   *Nota: O Vite empacotará os chunks da PWA e gerará a pasta `dist/` com o manifest e service worker compilados.*

---

## 3. Validação Pós-Deploy

Logo após a subida dos servidores:

1. **Checagem de Saúde Básica**:
   Acesse no navegador: `https://api.capio.app/api/health/`.
   Certifique-se de que a resposta é `200 OK` e que a conexão com o banco está ativa (`"database": "ok"`).
2. **Instalação da PWA**:
   Acesse o app, verifique se o ícone de instalação progressiva ("Guardar este espaço") funciona em conexões HTTPS.
3. **Validação do Service Worker**:
   Nos Developer Tools, confirme se o Service Worker v1.3.0 foi registrado com sucesso e está controlando a página.
4. **Auditoria de Conexão Offline**:
   Ative o "Modo Avião" ou desative a aba network. O app deve continuar navegável através dos fallbacks baseados no IndexedDB.
5. **Auditoria de Logs**:
   Abra os logs do Celery Worker e verifique a ausência de warnings de inicialização ou erros de conexão com o Redis.

---

## 4. Plano de Rollback de Contingência

Caso ocorram bugs críticos em produção, siga os passos de reversão rápida:

### 4.1 Rollback de Código e Deploy
1. **Identificar commit estável anterior**:
   ```bash
   git log -n 5 --oneline
   ```
2. **Reverter a branch principal**:
   ```bash
   git revert <commit_hash>
   # Ou faça o deploy apontando para a tag do release anterior (ex: v1.2.0)
   ```
3. **Disparar novo deploy no painel da nuvem**.

### 4.2 Rollback de Migrations (Se necessário)
Se a alteração de banco causou problemas e você precisa reverter:
1. Reverter o banco para a migration estável anterior (ex: `0003` do app users):
   ```bash
   python manage.py migrate users 0003
   ```
2. Caso tenha ocorrido corrupção severa, restaure o último backup de banco de dados (que deve ser configurado de forma diária automática no provedor PostgreSQL).

---

## 5. Testes Manuais pós-Deploy

| Item | Passo | Resultado Esperado |
| :--- | :--- | :--- |
| **Geração de Devocional** | Selecionar uma emoção na PWA. | A exegese bíblica canônica deve carregar e a IA deve produzir a oração em menos de 6s. |
| **Idempotência de Devocional** | Repetir a seleção da mesma emoção. | A resposta deve ser imediata (< 200ms) sem chamar a API da Anthropic, servindo do banco. |
| **Fallback de Rede** | Cortar a conexão física do PWA. | A badge "Espaço Offline" deve aparecer e apresentar a leitura do IndexedDB sem quebrar a tela. |
| **Inscrição de Push** | Ativar o seletor de horários. | A inscrição Web Push deve persistir no banco sem erros no log do Django. |
| **ErrorBoundary** | Simular erro no React. | O ErrorBoundary contemplativo deve renderizar perfeitamente a mensagem *"Algo ficou em silêncio por um instante."* |
