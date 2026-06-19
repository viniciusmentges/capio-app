import React from 'react';

export default function EditorialTitle({ children, as: Component = 'h2', className = '' }) {
  return <Component className={`editorial-title ${className}`}>{children}</Component>;
}
