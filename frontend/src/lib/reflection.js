import { api } from './api';

export async function getTodayReflection() {
  const { data } = await api.get('/api/reflection/today/');
  return data;
}

export async function respondTodayReflection(payload) {
  const { data } = await api.post('/api/reflection/today/respond/', payload);
  return data;
}

export async function getNightReflection() {
  const { data } = await api.get('/api/reflection/night/');
  return data;
}

export async function getLiturgicalArchive() {
  const { data } = await api.get('/api/reflection/liturgical-archive/');
  return data;
}

export async function getSpiritualJourney() {
  const { data } = await api.get('/api/reflection/spiritual-journey/');
  return data;
}
