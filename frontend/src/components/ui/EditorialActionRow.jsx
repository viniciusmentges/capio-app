import React from 'react';

export default function EditorialActionRow({ actions, className = "" }) {
  return (
    <div className={`flex flex-row items-center justify-center gap-8 w-full max-w-[280px] mx-auto pt-6 ${className}`}>
      {actions.map((action, index) => {
        const Icon = action.icon;
        return (
          <button 
            key={index}
            onClick={action.onClick}
            disabled={action.disabled}
            aria-label={action.ariaLabel || action.label}
            className="flex flex-col items-center justify-start space-y-3 group disabled:opacity-50"
          >
            <div className="w-12 h-12 shrink-0 rounded-full bg-foreground/5 flex items-center justify-center group-hover:bg-foreground/10 transition-colors">
              <Icon className="w-4 h-4 text-foreground/60" />
            </div>
            <span className="text-[9px] font-serif uppercase tracking-[0.2em] text-foreground/40 group-hover:text-foreground/60 transition-colors text-center leading-relaxed">
              {action.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
