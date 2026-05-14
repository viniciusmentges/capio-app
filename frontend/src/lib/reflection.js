import { api } from './api';

export async function getTodayReflection() {
  const { data } = await api.get('/api/reflection/today/');
  return data;
}

export async function respondTodayReflection(payload) {
  // O backend deve esperar um payload para responder/dar feedback
  // No Django, pode ser /api/reflection/today/respond/ ou /api/feedback/
  // Usando a especificação primária do prompt:
  const { data } = await api.post('/api/reflection/today/respond/', payload);
  return data;
}
