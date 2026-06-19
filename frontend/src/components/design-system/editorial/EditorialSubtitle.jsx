import React from 'react';

export default function EditorialSubtitle({ children, as: Component = 'h3', className = '' }) {
  return <Component className={`editorial-subtitle ${className}`}>{children}</Component>;
}
