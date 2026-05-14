import React, { useState } from 'react';
import { RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { router } from './router';
import { AuthProvider } from '../context/AuthContext';
import SplashScreen from '../components/layout/SplashScreen';

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

  if (showSplash) {
    return (
      <QueryClientProvider client={queryClient}>
        <SplashScreen onFinish={() => setShowSplash(false)} />
      </QueryClientProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
