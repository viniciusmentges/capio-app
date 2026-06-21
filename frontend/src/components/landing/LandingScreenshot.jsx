import React from 'react';

export default function LandingScreenshot({ src, alt, className = '' }) {
  return (
    <figure className={`w-full flex justify-center items-center my-32 px-6 md:px-0 ${className}`}>
      <img 
        src={src} 
        alt={alt} 
        loading="lazy"
        className="w-full max-w-xl object-contain rounded-sm shadow-none opacity-90 hover:opacity-100 transition-opacity duration-[2000ms] ease-in-out"
      />
    </figure>
  );
}
