import React from 'react';
import { Outlet } from 'react-router-dom';
import BottomNav from './BottomNav';
import ScrollToTop from './ScrollToTop';
import { useScrollDirection } from '../../hooks/useScrollDirection';

export default function AppShell() {
  const scrollDir = useScrollDirection();
  const isHidden = scrollDir === 'down';

  return (
    <div className="w-full min-h-[100dvh] bg-background text-foreground selection:bg-black/5 selection:text-foreground">
      <ScrollToTop />
      {/* Wordmark discreto no topo que desaparece no scroll para imersão */}
      <header className={`fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-sm py-8 flex justify-center transition-transform duration-500 ease-in-out ${isHidden ? '-translate-y-full' : 'translate-y-0'}`}>
        <h1 className="font-serif text-[10px] uppercase tracking-[0.4em] text-foreground/10">
          CAPIO
        </h1>
      </header>

      {/* Aumento do padding superior para compensar o header e o ritmo editorial */}
      <main className="mx-auto w-full max-w-xl px-6 pt-32 pb-[calc(10rem+env(safe-area-inset-bottom))] flex flex-col space-y-[var(--space-section)] min-h-[100dvh]">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
