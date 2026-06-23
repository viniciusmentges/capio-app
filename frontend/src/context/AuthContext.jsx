import React, { createContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../lib/auth';
import { getAccessToken, setTokens, clearTokens } from '../utils/tokenStorage';
import { ANALYTICS_EVENTS } from '../analytics/events';
import { captureEvent } from '../analytics/posthogClient';
import { captureException } from '../observability/sentry';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loadingAuth, setLoadingAuth] = useState(true);

  const performLogout = useCallback(() => {
    clearTokens();
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const loadUser = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      performLogout();
      setLoadingAuth(false);
      return;
    }

    try {
      const data = await authApi.getMe();
      setUser(data);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Falha ao carregar usuario:', error);
      captureException(error, {
        tags: { area: 'auth', action: 'load_user' },
      });
      performLogout();
    } finally {
      setLoadingAuth(false);
    }
  }, [performLogout]);

  useEffect(() => {
    loadUser();

    const handleAuthExpired = () => {
      performLogout();
    };

    window.addEventListener('auth-expired', handleAuthExpired);
    return () => window.removeEventListener('auth-expired', handleAuthExpired);
  }, [loadUser, performLogout]);

  const login = async (credentials) => {
    const response = await authApi.login(credentials);
    const access = response.access || response.data?.access;
    const refresh = response.refresh || response.data?.refresh;

    if (access) {
      setTokens(access, refresh);
      await loadUser();
    }

    captureEvent(ANALYTICS_EVENTS.USER_LOGGED_IN, {
      method: 'password',
    });
    return response;
  };

  const loginWithGoogle = async (token) => {
    const response = await authApi.googleLogin(token);
    const access = response.access || response.data?.access;
    const refresh = response.refresh || response.data?.refresh;

    if (access) {
      setTokens(access, refresh);
      await loadUser();
    }

    captureEvent(ANALYTICS_EVENTS.USER_LOGGED_IN, {
      method: 'google',
    });
    return response;
  };

  const register = async (userData) => {
    const response = await authApi.register(userData);
    const access = response.access || response.data?.access;
    const refresh = response.refresh || response.data?.refresh;

    if (access) {
      setTokens(access, refresh);
      await loadUser();
    }

    captureEvent(ANALYTICS_EVENTS.USER_REGISTERED, {
      method: 'password',
    });
    return response;
  };

  const logout = () => {
    performLogout();
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      loadingAuth,
      login,
      loginWithGoogle,
      register,
      logout,
      loadUser
    }}>
      {children}
    </AuthContext.Provider>
  );
}
