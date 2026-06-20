import React from 'react';

export default function EditorialNavigation({
  prevText,
  nextText,
  onPrev,
  onNext,
  className = ""
}) {
  return (
    <div className={`flex items-center justify-between w-full gap-4 ${className}`}>
      <div className="flex-1 flex justify-start overflow-hidden">
        {prevText && onPrev && (
          <button 
            onClick={onPrev} 
            className="font-serif text-[10px] text-accent hover:opacity-70 transition-opacity uppercase tracking-widest whitespace-nowrap truncate text-left"
          >
            <span className="mr-1">&larr;</span> {prevText}
          </button>
        )}
      </div>
      <div className="flex-1 flex justify-end overflow-hidden">
        {nextText && onNext && (
          <button 
            onClick={onNext} 
            className="font-serif text-[10px] text-accent hover:opacity-70 transition-opacity uppercase tracking-widest whitespace-nowrap truncate text-right"
          >
            {nextText} <span className="ml-1">&rarr;</span>
          </button>
        )}
      </div>
    </div>
  );
}
