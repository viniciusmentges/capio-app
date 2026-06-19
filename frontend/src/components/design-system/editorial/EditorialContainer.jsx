import React from 'react';

export default function EditorialContainer({ children, className = '' }) {
  return (
    <div className={`w-full max-w-4xl mx-auto box-border ${className}`}>
      {children}
    </div>
  );
}
