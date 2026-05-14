# Plataforma Devocional Católica com IA - Backend

Repositório backend da plataforma devocional católica com IA.

## Estrutura de Pastas

- `apps/`: Apps do Django (users, bible, devotional, reflection, ai_core)
- `services/`: Lógica de negócio e integrações
- `config/`: Configurações do projeto e roteamento principal

## Como rodar localmente

1. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   Copie o arquivo `.env.example` para `.env` e ajuste as variáveis.

4. Execute as migrações (se os models estiverem criados):
   ```bash
   python manage.py migrate
   ```

5. Inicie o servidor:
   ```bash
   python manage.py runserver
   ```

## Fluxo completo de teste

Para testar o MVP do zero, abra o terminal na pasta `backend` e rode:

1. **Configurar o banco de dados:**
   ```bash
   python manage.py migrate
   ```

2. **Popular os dados iniciais:**
   Carrega as emoções e cria um admin padrão (`admin` / `admin123`).
   ```bash
   python manage.py seed_initial_data
   ```

3. **Subir o servidor:**
   ```bash
   python manage.py runserver
   ```

4. **Testar os fluxos (em outro terminal):**
   *Veja o arquivo `docs/api_examples.md` para payloads exatos e sequências de requests para Registro, Login, Bíblia, Devocionais e Reflexão.*

## Rodando os Testes Automatizados

Para rodar todos os testes do sistema que garantem a segurança do app:
```bash
python manage.py test
```

## Configurando Inteligência Artificial (Anthropic)

O sistema por padrão utiliza um **Mock** (respostas pré-gravadas e hardcoded) para evitar custos durante o desenvolvimento frontend inicial.

Para ativar a IA real (Claude 3):
1. No arquivo `.env`, altere `USE_REAL_AI=True`.
2. Adicione sua chave de API: `ANTHROPIC_API_KEY=sk-ant-api03-...`.
3. (Opcional) Ajuste o modelo: `ANTHROPIC_MODEL=claude-haiku-4-5-20251001`.

**Para voltar ao mock:**
Apenas retorne `USE_REAL_AI=False` no `.env`. O sistema fará o chaveamento automático. Se a IA real falhar por qualquer motivo (falta de crédito, formato de resposta inválido), o sistema também fará **fallback silencioso** para o mock, garantindo que o usuário nunca receba um erro 500 no app.

> **Cuidado de Custos:** A ativação da API real incorre em custos na Anthropic. Como as requisições geram textos como devocionais, o uso contínuo pode consumir créditos rapidamente. Use a flag `USE_REAL_AI=True` preferencialmente em testes reais de integração ou produção.
