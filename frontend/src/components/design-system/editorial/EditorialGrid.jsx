import React from 'react';

export default function EditorialGrid({ children, className = '' }) {
  return (
    <div className={`grid grid-cols-1 gap-md w-full ${className}`}>
      {children}
    </div>
  );
}
