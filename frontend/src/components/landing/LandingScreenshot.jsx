import React from 'react';

export default function LandingScreenshot({ src, alt, placeholderText, className = '' }) {
  return (
    <figure className={`w-full flex justify-center items-center my-32 px-6 md:px-0 ${className}`}>
      {src ? (
        <img 
          src={src} 
          alt={alt} 
          loading="lazy"
          className="w-full max-w-xl object-contain rounded-sm shadow-none opacity-90 hover:opacity-100 transition-opacity duration-[2000ms] ease-in-out border border-border/40 bg-surface/50"
        />
      ) : (
        <div className="w-full max-w-xl aspect-[4/3] md:aspect-[16/10] bg-surface/40 border border-border flex items-center justify-center rounded-sm transition-opacity duration-[2000ms] ease-in-out">
          <p className="font-serif italic text-sm md:text-base text-foreground/40 tracking-wide text-center px-6">
            {placeholderText}
          </p>
        </div>
      )}
    </figure>
  );
}
