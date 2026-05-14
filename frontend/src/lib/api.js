import axios from 'axios';
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '../utils/tokenStorage';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: add access token
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Response Interceptor: handle 401 and refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Prevent loop and don't intercept auth routes
    if (
      !originalRequest || 
      error.response?.status !== 401 || 
      originalRequest._retry || 
      originalRequest.url?.includes('auth/refresh') ||
      originalRequest.url?.includes('auth/login')
    ) {
      return Promise.reject(error);
    }

    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      // Sem refresh token, impossível renovar
      clearTokens();
      window.dispatchEvent(new Event('auth-expired'));
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise(function(resolve, reject) {
        failedQueue.push({ resolve, reject });
      })
      .then(token => {
        originalRequest.headers.Authorization = 'Bearer ' + token;
        return api(originalRequest);
      })
      .catch(err => Promise.reject(err));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const response = await axios.post(`${baseURL}/api/auth/refresh/`, { refresh: refreshToken });
      const { access, refresh } = response.data;
      
      // Alguns backends só mandam access, outros mandam ambos
      setTokens(access, refresh || refreshToken);
      
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      originalRequest.headers.Authorization = `Bearer ${access}`;
      
      processQueue(null, access);
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      clearTokens();
      window.dispatchEvent(new Event('auth-expired'));
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);
