import React from 'react';

export default function EditorialDivider({ variant = "line", className = "", children }) {
  if (variant === "content") {
    return (
      <div className={`flex items-center justify-center space-x-6 opacity-60 ${className}`}>
        <div className="h-px bg-border flex-grow" />
        {children}
        <div className="h-px bg-border flex-grow" />
      </div>
    );
  }
  
  if (variant === "dot") {
    return <div className={`w-1 h-1 bg-border rounded-full mx-auto ${className}`} />;
  }

  return <div className={`w-6 h-px bg-border mx-auto ${className}`} />;
}
