import React, { useEffect, useState } from 'react';
import { useStandaloneMode } from '../../hooks/useStandaloneMode';

export default function EditorialSplash({ onFinish }) {
  const isStandalone = useStandaloneMode();
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    // Verificar se já exibimos o splash nesta sessão para evitar fadiga visual
    const alreadyShown = sessionStorage.getItem('capio_splash_shown');
    
    // Se for acessado no navegador comum e já foi exibido, pulamos instantaneamente
    if (!isStandalone && alreadyShown) {
      onFinish();
      return;
    }

    // Tempos refinados e silenciosos
    // 1800ms se for primeiro acesso em standalone, 600ms se for recorrente ou comum
    const displayDuration = alreadyShown ? 600 : 1800; 
    const fadeDuration = 800; // Animação macia de saída

    const showTimer = setTimeout(() => {
      setVisible(false); // Inicia fade-out de opacidade
      sessionStorage.setItem('capio_splash_shown', 'true');
      
      const finishTimer = setTimeout(() => {
        onFinish();
      }, fadeDuration);
      
      return () => clearTimeout(finishTimer);
    }, displayDuration);

    return () => clearTimeout(showTimer);
  }, [onFinish, isStandalone]);

  return (
    <div
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center transition-opacity ease-out"
      style={{
        transitionDuration: '800ms',
        opacity: visible ? 1 : 0,
        backgroundColor: '#F8F7F4', // Fundo editorial oficial
      }}
    >
      <div className="space-y-4 text-center">
        <h1 className="font-serif text-sm tracking-[0.4em] uppercase text-foreground/35 animate-fade-in-title">
          CAPIO
        </h1>
        <p 
          className="font-serif italic text-xs text-foreground/20 tracking-wide"
          style={{
            animation: 'fade-in-subtitle 1.4s ease-out forwards',
            opacity: 0,
          }}
        >
          Respire.
        </p>
      </div>

      <style>{`
        @keyframes fade-in-subtitle {
          0% { opacity: 0; transform: translateY(4px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-title {
          animation: fade-in-title-anim 1s ease-out forwards;
        }
        @keyframes fade-in-title-anim {
          0% { opacity: 0; transform: translateY(6px); }
          100% { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
