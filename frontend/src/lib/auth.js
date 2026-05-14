import { api } from './api';

export const authApi = {
  async register(payload) {
    const response = await api.post('/api/auth/register/', payload);
    return response.data;
  },

  async login(payload) {
    const response = await api.post('/api/auth/login/', payload);
    return response.data;
  },

  async refreshToken(refresh) {
    const response = await api.post('/api/auth/refresh/', { refresh });
    return response.data;
  },

  async getMe() {
    const response = await api.get('/api/auth/me/');
    return response.data;
  }
};
