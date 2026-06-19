import React from 'react';

export default function EditorialActionRow({ children, className = '' }) {
  return (
    <div className={`grid grid-cols-3 gap-sm items-start justify-items-center w-full pt-md ${className}`}>
      {children}
    </div>
  );
}
