import React from 'react';

export default function EditorialLabel({ children, className = "" }) {
  return (
    <p className={`text-[9px] font-serif italic text-accent text-center tracking-[0.2em] uppercase ${className}`}>
      {children}
    </p>
  );
}
