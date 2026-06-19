import React from 'react';

export default function EditorialNavigation({ prevTitle, onPrev, nextTitle, onNext, className = '' }) {
  return (
    <div className={`flex items-center justify-between w-full pt-md flex-nowrap gap-sm ${className}`}>
      {onPrev ? (
        <button onClick={onPrev} className="editorial-label hover:opacity-70 transition-opacity truncate flex-1 text-left">
          &larr; {prevTitle}
        </button>
      ) : <div className="flex-1" />}
      
      {onNext ? (
        <button onClick={onNext} className="editorial-label hover:opacity-70 transition-opacity truncate flex-1 text-right">
          {nextTitle} &rarr;
        </button>
      ) : <div className="flex-1" />}
    </div>
  );
}
