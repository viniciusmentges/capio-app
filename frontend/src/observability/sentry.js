import * as Sentry from '@sentry/react';

const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;

export function initSentry() {
  if (!SENTRY_DSN) return;

  Sentry.init({
    dsn: SENTRY_DSN,
    environment: import.meta.env.MODE,
    release: import.meta.env.VITE_APP_VERSION,
    sendDefaultPii: false,
    tracesSampleRate: Number(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || 0.05),
    integrations: [],
  });
}

export function captureException(error, context = {}) {
  if (!error) return;

  if (!SENTRY_DSN) {
    console.error('[CAPIO Observability]', error, context);
    return;
  }

  Sentry.captureException(error, context);
}

export { Sentry };
