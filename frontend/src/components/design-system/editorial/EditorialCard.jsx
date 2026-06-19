import React, { forwardRef } from 'react';

const EditorialCard = forwardRef(({ children, className = '', ...props }, ref) => {
  return (
    <div 
      ref={ref}
      className={`bg-surface border border-border rounded-xl p-lg md:p-xl shadow-[0_4px_24px_rgba(42,41,38,0.02)] w-full box-border ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});

EditorialCard.displayName = 'EditorialCard';
export default EditorialCard;
