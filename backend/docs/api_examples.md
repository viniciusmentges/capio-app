# Exemplos de API

Aqui estão as coleções de chamadas para testar a API. As rotas protegidas precisam do Header `Authorization: Bearer <seu_token>`.

## 1. Auth & Usuários

### Registrar Usuário
```http
POST /api/auth/register/
Content-Type: application/json

{
  "username": "fiel1",
  "email": "fiel1@email.com",
  "password": "securepass123",
  "diocese": "Arquidiocese de São Paulo"
}
```

### Login (Obter Token)
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "fiel1",
  "password": "securepass123"
}
```
**Resposta esperada:** Retorna `access` e `refresh` tokens.

---

## 2. Bíblia

### Pedir Explicação
```http
POST /api/bible/explain/
Authorization: Bearer <seu_token>
Content-Type: application/json

{
  "reference": "João 3:16"
}
```

### Exemplo de Hard Block (Bloqueio)
```http
POST /api/bible/explain/
Authorization: Bearer <seu_token>
Content-Type: application/json

{
  "reference": "Feitiçaria e magia negra"
}
```
**Resposta esperada:** HTTP 422
```json
{
  "error": "content_blocked",
  "category": "inappropriate_content",
  "message": "Content blocked."
}
```

---

## 3. Devocional

### Listar Emoções
```http
GET /api/devotional/emotions/
Authorization: Bearer <seu_token>
```

### Gerar Devocional por Emoção
```http
POST /api/devotional/by-emotion/
Authorization: Bearer <seu_token>
Content-Type: application/json

{
  "emotion_slug": "ansioso"
}
```

---

## 4. Reflexão Diária

### Pegar a Reflexão de Hoje
```http
GET /api/reflection/today/
Authorization: Bearer <seu_token>
```

### Responder à Reflexão
```http
POST /api/reflection/today/respond/
Authorization: Bearer <seu_token>
Content-Type: application/json

{
  "response_text": "Me tocou profundamente, vou tentar amar mais minha família hoje."
}
```

---

## 5. Feedback

### Enviar Feedback sobre uma passagem/devocional
```http
POST /api/feedback/
Authorization: Bearer <seu_token>
Content-Type: application/json

{
  "response_type": "BIBLE",
  "content_ref_id": 1,
  "helpful": true,
  "comment": "Muito claro e objetivo."
}
```
