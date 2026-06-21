import React, { useState } from 'react';

export default function LandingScreenshot({ src, alt, placeholderText, className = '', isNight = false, variant = 'card' }) {
  const [hasError, setHasError] = useState(false);

  // Variantes de exibição
  const isImmersive = variant === 'immersive';

  // Cores da moldura caso não seja imersivo
  const bgClass = isNight ? 'bg-background/20' : 'bg-surface';
  const borderClass = isNight ? 'border-border/10' : 'border-border/40';

  // Se for imersivo, removemos padding e bordas grossas,
  // permitindo que a imagem (que tem a mesma cor de fundo da página) 
  // sangre livremente pelo container sem parecer "encaixotada".
  const containerClasses = isImmersive 
    ? 'relative w-full overflow-hidden flex justify-center'
    : `relative w-full rounded-sm overflow-hidden border ${borderClass} ${bgClass} p-2 md:p-3 shadow-sm transition-all duration-[2000ms]`;

  const imageClasses = isImmersive
    ? 'w-full max-w-[320px] md:max-w-[380px] object-contain opacity-95 hover:opacity-100 transition-opacity duration-700 ease-in-out'
    : 'w-full object-contain rounded-sm opacity-95 hover:opacity-100 transition-opacity duration-700 ease-in-out';

  return (
    <figure className={`w-full flex justify-center items-center ${className}`}>
      {src && !hasError ? (
        <div className={containerClasses}>
           <img 
            src={src} 
            alt={alt} 
            loading="lazy"
            onError={() => setHasError(true)}
            className={imageClasses}
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
