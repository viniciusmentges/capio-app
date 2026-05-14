import React from 'react';

const Button = React.forwardRef(({ className = '', variant = 'primary', children, ...props }, ref) => {
  const baseStyles = "inline-flex items-center justify-center rounded-xl px-6 py-3.5 text-sm font-medium transition-colors focus:outline-none focus:ring-1 focus:ring-foreground/10 disabled:opacity-40 disabled:pointer-events-none active:opacity-90";
  
  const variants = {
    primary: "bg-[var(--color-brand)] text-[var(--color-background)] hover:opacity-90",
    outline: "border border-[var(--color-border)] bg-transparent text-foreground hover:bg-foreground/[0.02]",
    ghost: "bg-transparent text-foreground hover:bg-foreground/[0.02]"
  };

  return (
    <button
      ref={ref}
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';
export default Button;
