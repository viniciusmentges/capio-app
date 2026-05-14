import React from 'react';

export default function EmptyState({ message = 'Um espaço de silêncio.' }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <p className="font-serif text-lg text-foreground/40 tracking-[0.01em] leading-relaxed max-w-sm mx-auto">
        {message}
      </p>
    </div>
  );
}
