import React from 'react';

export default function BibleSection({ editorial, children }) {
  if (!children) return null;
  return (
    <div className="space-y-6">
      {editorial && (
        <p className="text-[10px] font-serif italic text-foreground/20 text-center tracking-widest">
          {editorial}
        </p>
      )}
      <div className="text-contemplative text-foreground/80 whitespace-pre-wrap">
        {children}
      </div>
    </div>
  );
}
