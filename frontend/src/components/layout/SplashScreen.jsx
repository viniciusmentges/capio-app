import React, { useEffect, useState } from 'react';

export default function SplashScreen({ onFinish }) {
  const [exit, setExit] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setExit(true);
      setTimeout(onFinish, 1200); // Espera o fade de saída
    }, 2000); // Tempo de exibição
    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <div className={`fixed inset-0 z-[100] bg-background flex items-center justify-center transition-opacity duration-[1200ms] ease-out ${exit ? 'opacity-0' : 'opacity-100'}`}>
      <h1 className="font-serif text-sm tracking-[0.3em] uppercase text-foreground/40 animate-fade-in">
        CAPIO
      </h1>
    </div>
  );
}
