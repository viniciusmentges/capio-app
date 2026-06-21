import React, { useState } from 'react';

export default function LandingScreenshot({ src, alt, placeholderText, className = '', isNight = false }) {
  const [hasError, setHasError] = useState(false);

  // O "papel" de fundo do screenshot para criar profundidade.
  // Se for noturno, o bg-surface é diferente.
  const bgClass = isNight ? 'bg-background/20' : 'bg-surface';
  const borderClass = isNight ? 'border-border/10' : 'border-border/40';

  return (
    <figure className={`w-full flex justify-center items-center ${className}`}>
      {src && !hasError ? (
        <div className={`relative w-full rounded-sm overflow-hidden border ${borderClass} ${bgClass} p-2 md:p-3 shadow-sm transition-all duration-[2000ms]`}>
           <img 
            src={src} 
            alt={alt} 
            loading="lazy"
            onError={() => setHasError(true)}
            className="w-full object-contain rounded-sm opacity-95 hover:opacity-100 transition-opacity duration-700 ease-in-out"
          />
        </div>
      ) : (
        <div className={`w-full aspect-[4/3] md:aspect-[16/10] ${bgClass} border ${borderClass} flex items-center justify-center rounded-sm transition-opacity duration-[2000ms] ease-in-out p-6`}>
          <p className="font-serif italic text-sm text-foreground/40 tracking-wide text-center">
            {placeholderText}
          </p>
        </div>
      )}
    </figure>
  );
}
