import React from 'react';
import EditorialTitle from './EditorialTitle';

export default function EditorialSection({ title, children, className = '' }) {
  return (
    <section className={`py-xl w-full box-border ${className}`}>
      {title && (
        <div className="mb-md">
          <EditorialTitle>{title}</EditorialTitle>
        </div>
      )}
      {children}
    </section>
  );
}
