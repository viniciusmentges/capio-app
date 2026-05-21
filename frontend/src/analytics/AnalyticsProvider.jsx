import React, { createContext, useContext, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { ANALYTICS_EVENTS } from './events';
import { captureEvent, identifyUser, initPostHog, resetAnalytics } from './posthogClient';
import { captureException } from '../observability/sentry';

const AnalyticsContext = createContext({
  track: captureEvent,
});

export function AnalyticsProvider({ children }) {
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    initPostHog();
  }, []);

  useEffect(() => {
    if (isAuthenticated && user) {
      identifyUser(user);
    } else if (!isAuthenticated) {
      resetAnalytics();
    }
  }, [isAuthenticated, user]);

  useEffect(() => {
    const handleInstalled = () => {
      captureEvent(ANALYTICS_EVENTS.PWA_INSTALLED);
    };

    const handleServiceWorkerMessage = (event) => {
      if (event.data?.type === 'CAPIO_SW_ERROR') {
        captureException(new Error(event.data.message || 'Service worker failure'), {
          tags: { area: 'service_worker' },
          extra: event.data,
        });
      }
    };

    window.addEventListener('appinstalled', handleInstalled);
    navigator.serviceWorker?.addEventListener('message', handleServiceWorkerMessage);

    return () => {
      window.removeEventListener('appinstalled', handleInstalled);
      navigator.serviceWorker?.removeEventListener('message', handleServiceWorkerMessage);
    };
  }, []);

  return (
    <AnalyticsContext.Provider value={{ track: captureEvent }}>
      {children}
    </AnalyticsContext.Provider>
  );
}

export function useAnalytics() {
  return useContext(AnalyticsContext);
}
