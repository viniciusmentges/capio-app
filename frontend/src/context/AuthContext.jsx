import React, { createContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../lib/auth';
import { getAccessToken, setTokens, clearTokens } from '../utils/tokenStorage';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  // Inicializamos em true para evitar flicker; só passará a false após a primeira checagem
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
      console.error('Falha ao carregar usuário:', error);
      performLogout();
    } finally {
      setLoadingAuth(false);
    }
  }, [performLogout]);

  useEffect(() => {
    loadUser();

    // Escuta evento de expiração disparado pelo axios interceptor
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
      register,
      logout,
      loadUser
    }}>
      {children}
    </AuthContext.Provider>
  );
}
