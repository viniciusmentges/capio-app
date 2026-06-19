import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import BottomNav from './BottomNav';
import ScrollToTop from './ScrollToTop';
import { useScrollDirection } from '../../hooks/useScrollDirection';
import EditorialSkeleton from './EditorialSkeleton';
import { useStandaloneMode } from '../../hooks/useStandaloneMode';
import PWAUpdatePrompt from './PWAUpdatePrompt';

export default function AppShell() {
  const scrollDir = useScrollDirection();
  const isHidden = scrollDir === 'down';
  const location = useLocation();
  const isStandalone = useStandaloneMode();

  return (
    <div className="w-full min-h-[100dvh] bg-background text-foreground selection:bg-black/5 selection:text-foreground overscroll-behavior-y-contain mobile-shell standalone-shell">
      <ScrollToTop />
      {/* Wordmark discreto no topo que desaparece no scroll para imersão */}
      <header 
        className={`fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-sm flex justify-center transition-transform duration-500 ease-in-out ${isHidden ? '-translate-y-full' : 'translate-y-0'}`}
        style={{
          paddingTop: 'calc(2rem + env(safe-area-inset-top, 0px))',
          paddingBottom: '2rem',
        }}
      >
        <h1 className="font-serif text-[10px] uppercase tracking-[0.4em] text-foreground/10">
          CAPIO
        </h1>
      </header>

      {/* Aumento do padding superior para compensar o header e o ritmo editorial */}
      <main 
        className="mx-auto w-full max-w-xl px-6 flex flex-col space-y-[var(--space-section)] min-h-[100dvh]"
        style={{
          paddingTop: 'calc(8rem + env(safe-area-inset-top, 0px))',
          paddingBottom: 'calc(10rem + env(safe-area-inset-bottom, 16px))',
        }}
      >
        {/* Container animado com base na rota para efeito suave de respiração */}
        <div key={location.pathname} className="animate-fade-in w-full flex flex-col flex-1">
          <React.Suspense fallback={<EditorialSkeleton />}>
            <Outlet />
          </React.Suspense>
        </div>
      </main>
      <BottomNav />
      <PWAUpdatePrompt />
    </div>
  );
}
