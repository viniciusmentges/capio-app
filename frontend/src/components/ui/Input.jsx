import React from 'react';

const Input = React.forwardRef(({ className = '', ...props }, ref) => {
  return (
    <input
      ref={ref}
      className={`flex w-full rounded-xl border border-foreground/10 bg-transparent px-4 py-3 text-sm transition-colors placeholder:text-foreground/40 focus:outline-none focus:border-foreground/30 focus:ring-1 focus:ring-foreground/30 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    />
  );
});

Input.displayName = 'Input';
export default Input;
