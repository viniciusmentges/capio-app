import React from 'react';

export default function ErrorState({ message = 'Não foi possível carregar.' }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div className="w-8 h-px bg-foreground/10 mb-8" />
      <p className="font-serif text-lg text-foreground/50 tracking-[0.01em] leading-relaxed max-w-sm mx-auto">
        {message}
      </p>
    </div>
  );
}
