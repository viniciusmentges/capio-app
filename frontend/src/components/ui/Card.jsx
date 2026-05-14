import React from 'react';

const Card = React.forwardRef(({ className = '', children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={`rounded-3xl bg-[var(--color-surface)] p-8 md:p-12 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});

Card.displayName = 'Card';
export default Card;
