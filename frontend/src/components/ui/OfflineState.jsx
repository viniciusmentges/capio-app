import React from 'react';
import Button from './Button';

export default function OfflineState({ onRetry }) {
  return (
    <div className="flex flex-col justify-center items-center min-h-[60vh] px-6 text-center space-y-16 animate-fade-in-fast">
      {/* Elemento visual minimalista e contemplativo: um círculo sutil de presença */}
      <div className="relative flex items-center justify-center">
        <div className="w-16 h-16 rounded-full border border-foreground/5 animate-pulse" />
        <div className="absolute w-4 h-4 rounded-full bg-foreground/10" />
      </div>

      <div className="space-y-6 max-w-sm">
        <h2 className="font-serif text-2xl text-foreground/80 tracking-tight">
          Espaço de Recolhimento
        </h2>
        <p className="font-serif italic text-sm text-foreground/45 leading-relaxed">
          Você está offline. A CAPIO convida você a guardar este momento para o silêncio, a respiração e a presença simples.
        </p>
        <p className="text-[10px] uppercase tracking-[0.2em] text-foreground/35">
          Suas reflexões retornarão com a conexão.
        </p>
      </div>

      {onRetry && (
        <Button
          onClick={onRetry}
          className="py-3 px-8 text-[10px] uppercase tracking-[0.2em] border border-foreground/10 hover:border-foreground/30 bg-transparent text-foreground/60 hover:text-foreground/90 transition-all rounded-none"
        >
          Reconectar
        </Button>
      )}
    </div>
  );
}
