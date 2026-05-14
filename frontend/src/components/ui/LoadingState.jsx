import React from 'react';

export default function LoadingState({ message = 'Silenciando o coração...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-foreground/20">
      <div className="w-8 h-px bg-foreground/5 mb-6" />
      <p className="font-serif text-base italic tracking-wide animate-fade-in duration-500">
        {message}
      </p>

    </div>
  );
}
