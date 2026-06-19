import React from 'react';

export default function EditorialDivider({ variant = 'line', className = '' }) {
  if (variant === 'dot') {
    return (
      <div className={`flex justify-center py-lg ${className}`}>
        <div className="w-1 h-1 bg-border rounded-full" />
      </div>
    );
  }
  
  if (variant === 'short') {
    return (
      <div className={`flex justify-center py-md ${className}`}>
        <div className="w-8 h-px bg-border" />
      </div>
    );
  }

  // line
  return (
    <div className={`py-lg flex items-center w-full opacity-60 ${className}`}>
      <div className="w-full h-px bg-border" />
    </div>
  );
}
