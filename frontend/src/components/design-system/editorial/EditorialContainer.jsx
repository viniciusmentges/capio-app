import React from 'react';

export default function EditorialContainer({ children, className = '' }) {
  return (
    <div className={`mobile-shell safe-x max-w-4xl mx-auto safe-bottom safe-top ${className}`}>
      {children}
    </div>
  );
}
