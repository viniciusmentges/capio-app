import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import { useAuth } from '../hooks/useAuth';
import LoadingState from '../components/ui/LoadingState';

import HomePage from '../pages/home/HomePage';
import EmotionPage from '../pages/devotional/EmotionPage';
import BibleExplainPage from '../pages/bible/BibleExplainPage';
import TodayReflectionPage from '../pages/reflection/TodayReflectionPage';
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loadingAuth } = useAuth();

  if (loadingAuth) {
    return (
      <div className="min-h-[100dvh] bg-background flex flex-col justify-center">
        <LoadingState />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function PublicRoute({ children }) {
  const { isAuthenticated, loadingAuth } = useAuth();

  if (loadingAuth) {
    return (
      <div className="min-h-[100dvh] bg-background flex flex-col justify-center">
        <LoadingState />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
}

import SharedContentViewer from '../pages/public/SharedContentViewer';

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      {
        path: "/",
        element: <HomePage />
      },
      {
        path: "/devotional/emotions",
        element: <EmotionPage />
      },
      {
        path: "/bible/explain",
        element: <BibleExplainPage />
      },
      {
        path: "/reflection/today",
        element: <TodayReflectionPage />
      }
    ]
  },
  {
    path: "/share/:type/:id",
    element: <SharedContentViewer />
  },
  {
    path: "/login",
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    )
  },
  {
    path: "/register",
    element: (
      <PublicRoute>
        <RegisterPage />
      </PublicRoute>
    )
  }
]);

