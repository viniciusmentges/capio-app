const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export function getAccessToken() {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }
  return null;
}

export function getRefreshToken() {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }
  return null;
}

export function setTokens(access, refresh) {
  if (typeof window !== 'undefined') {
    if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  }
}

export function clearTokens() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}
