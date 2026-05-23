import posthog from 'posthog-js';

const POSTHOG_KEY = import.meta.env.VITE_POSTHOG_KEY;
const POSTHOG_HOST = import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com';
const IS_BROWSER = typeof window !== 'undefined';

let initialized = false;

export function initPostHog() {
  if (!IS_BROWSER || initialized || !POSTHOG_KEY) {
    return initialized;
  }

  try {
    posthog.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      autocapture: false,
      capture_pageview: false,
      capture_pageleave: false,
      disable_session_recording: true,
      respect_dnt: true,
      persistence: 'localStorage+cookie',
      loaded: () => {
        initialized = true;
      },
    });
    initialized = true;
  } catch (error) {
    initialized = false;
    console.error('[CAPIO Analytics] Falha ao inicializar PostHog:', error);
  }

  return initialized;
}

export function captureEvent(eventName, properties = {}) {
  if (!IS_BROWSER || !eventName) return;

  try {
    if (!initialized) {
      initPostHog();
    }

    if (!initialized) return;

    posthog.capture(eventName, {
      app: 'capio',
      is_pwa: window.matchMedia?.('(display-mode: standalone)').matches || window.navigator.standalone === true,
      is_online: window.navigator.onLine,
      ...properties,
    });
  } catch (error) {
    console.error('[CAPIO Analytics] Falha ao registrar evento:', error);
  }
}

export function identifyUser(user) {
  if (!IS_BROWSER || !user) return;

  try {
    if (!initialized) {
      initPostHog();
    }

    if (!initialized) return;

    const distinctId = user.id || user.pk || user.email || user.username;
    if (!distinctId) return;

    posthog.identify(String(distinctId), {
      has_email: Boolean(user.email),
      has_diocese: Boolean(user.diocese),
    });
  } catch (error) {
    console.error('[CAPIO Analytics] Falha ao identificar usuário:', error);
  }
}

export function capturePageView(pathname) {
  if (!IS_BROWSER) return;

  try {
    if (!initialized) {
      initPostHog();
    }

    if (!initialized) return;

    posthog.capture('$pageview', { $current_url: window.location.origin + pathname });
  } catch (error) {
    console.error('[CAPIO Analytics] Falha ao registrar pageview:', error);
  }
}

export function resetAnalytics() {
  if (!IS_BROWSER || !initialized) return;

  try {
    posthog.reset();
  } catch (error) {
    console.error('[CAPIO Analytics] Falha ao limpar identificação:', error);
  }
}
