import { api } from '../lib/api';

export async function explainBiblePassage(payload) {
  // Payload esperado: { reference: passage } ou { passage: passage }
  // O backend atual espera 'reference', mas aceitaremos ambos e mapearemos se necessário.
  const reference = payload.reference || payload.passage;
  const { data } = await api.post('/api/bible/explain/', { reference });
  return data;
}

export async function getBibleHistory() {
  const { data } = await api.get('/api/bible/history/');
  return data;
}
