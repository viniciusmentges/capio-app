import { api } from '../lib/api';

export async function getEmotions() {
  const { data } = await api.get('/api/devotional/emotions/');
  return data;
}

export async function getDevotionalByEmotion(payload) {
  // O backend espera 'emotion_slug', mas o frontend pode passar 'emotion'
  const emotion_slug = payload.emotion_slug || payload.emotion;
  const { data } = await api.post('/api/devotional/by-emotion/', { emotion_slug });
  return data;
}
