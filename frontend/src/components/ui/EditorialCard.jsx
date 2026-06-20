import React from 'react';

export default function EditorialCard({ 
  variant = 'default', 
  className = '', 
  children 
}) {
  // O EditorialCard controla fundo, borda suave, radius, padding interno e ausência de sombra agressiva.
  const baseClasses = "rounded-sm px-8 py-12 border shadow-none";
  
  const variants = {
    default: "bg-background border-border/60",
    focus: "bg-surface border-border",
    subtle: "bg-transparent border-border/30"
  };

  const variantClasses = variants[variant] || variants.default;

  return (
    <div className={`${baseClasses} ${variantClasses} ${className}`}>
      {children}
    </div>
  );
}
