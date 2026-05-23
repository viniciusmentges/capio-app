import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import { capturePageView } from '../analytics/posthogClient';
import { useAuth } from '../hooks/useAuth';
import LoadingState from '../components/ui/LoadingState';

const HomePage = React.lazy(() => import('../pages/home/HomePage'));
const EmotionPage = React.lazy(() => import('../pages/devotional/EmotionPage'));
const BibleExplainPage = React.lazy(() => import('../pages/bible/BibleExplainPage'));
const TodayReflectionPage = React.lazy(() => import('../pages/reflection/TodayReflectionPage'));
const LoginPage = React.lazy(() => import('../pages/auth/LoginPage'));
const RegisterPage = React.lazy(() => import('../pages/auth/RegisterPage'));

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

const SharedContentViewer = React.lazy(() => import('../pages/public/SharedContentViewer'));
const SupportPage = React.lazy(() => import('../pages/support/SupportPage'));
const ForgotPasswordPage = React.lazy(() => import('../pages/auth/ForgotPasswordPage'));

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
    path: "/apoie",
    element: <SupportPage />
  },
  {
    path: "/recuperar-senha",
    element: <ForgotPasswordPage />
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

let lastTrackedPath = null;
router.subscribe((state) => {
  const pathname = state.location.pathname;
  if (pathname !== lastTrackedPath) {
    lastTrackedPath = pathname;
    capturePageView(pathname);
  }
});

