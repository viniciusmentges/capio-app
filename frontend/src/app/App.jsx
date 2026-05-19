import React, { useState } from 'react';
import { RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { router } from './router';
import { AuthProvider } from '../context/AuthContext';
import { TextSizeProvider } from '../context/TextSizeContext';
import EditorialSplash from '../components/pwa/EditorialSplash';
import ErrorBoundary from '../components/ui/ErrorBoundary';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const [showSplash, setShowSplash] = useState(true);

  React.useEffect(() => {
    // Incrementar contador de sessões reais na montagem (PWA)
    if (!sessionStorage.getItem('capio_session_active')) {
      sessionStorage.setItem('capio_session_active', 'true');
      const count = parseInt(localStorage.getItem('capio_session_count') || '0', 10);
      localStorage.setItem('capio_session_count', (count + 1).toString());
      console.log(`Nova sessão CAPIO iniciada. Total de sessões acumuladas: ${count + 1}`);
    }
  }, []);

  if (showSplash) {
    return (
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <EditorialSplash onFinish={() => setShowSplash(false)} />
        </QueryClientProvider>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <TextSizeProvider>
            <RouterProvider router={router} />
          </TextSizeProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
