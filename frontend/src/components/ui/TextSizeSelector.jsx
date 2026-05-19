import React from 'react';
import { useTextSize } from '../../context/TextSizeContext';

export default function TextSizeSelector() {
  const { textSize, setTextSize } = useTextSize();

  const options = [
    { value: 'sm', label: 'A-' },
    { value: 'base', label: 'A' },
    { value: 'lg', label: 'A+' }
  ];

  return (
    <div className="flex items-center justify-center space-x-4 py-2 px-4 rounded-full bg-foreground/[0.02] border border-foreground/[0.04] w-fit mx-auto animate-fade-in-fast mb-6">
      {options.map((opt, i) => (
        <React.Fragment key={opt.value}>
          {i > 0 && <span className="text-[8px] text-foreground/20 font-light">•</span>}
          <button
            onClick={() => setTextSize(opt.value)}
            className={`text-xs font-serif tracking-widest transition-all duration-300 px-2 py-0.5 rounded-sm ${
              textSize === opt.value
                ? 'text-foreground font-semibold scale-110'
                : 'text-foreground/35 hover:text-foreground/60'
            }`}
            aria-label={`Tamanho de texto ${opt.label}`}
          >
            {opt.label}
          </button>
        </React.Fragment>
      ))}
    </div>
  );
}
