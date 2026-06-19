import React from 'react';

export default function EditorialLabel({ children, className = '' }) {
  return <p className={`editorial-label ${className}`}>{children}</p>;
}
