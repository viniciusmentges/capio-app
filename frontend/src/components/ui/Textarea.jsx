import React from 'react';

const Textarea = React.forwardRef(({ className = '', ...props }, ref) => {
  return (
    <textarea
      ref={ref}
      className={`flex min-h-[120px] w-full rounded-xl border border-foreground/10 bg-transparent px-4 py-3 text-sm transition-colors placeholder:text-foreground/40 focus:outline-none focus:border-foreground/30 focus:ring-1 focus:ring-foreground/30 disabled:cursor-not-allowed disabled:opacity-50 resize-none ${className}`}
      {...props}
    />
  );
});

Textarea.displayName = 'Textarea';
export default Textarea;
