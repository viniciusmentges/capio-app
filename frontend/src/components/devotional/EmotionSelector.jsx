import React from 'react';

export function EmotionCard({ emotion, isSelected, onSelect }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(emotion.slug)}
      className={`w-full text-left p-6 rounded-2xl transition-all duration-300 border relative z-10 ${
        isSelected 
          ? 'bg-surface border-brand/20 text-brand ring-1 ring-brand/5 shadow-sm' 
          : 'bg-transparent border-border text-foreground/50 hover:border-brand/20 hover:bg-surface'
      }`}
    >
      <span className={`font-serif text-lg tracking-wide transition-colors duration-300 ${isSelected ? 'opacity-100' : 'opacity-80'}`}>
        {emotion.name}
      </span>
    </button>
  );
}

export default function EmotionSelector({ emotions, selectedSlug, onSelect }) {
  if (!emotions || emotions.length === 0) return null;

  return (
    <div className="grid grid-cols-1 gap-3 relative">
      {emotions.map((emotion) => (
        <EmotionCard
          key={emotion.slug}
          emotion={emotion}
          isSelected={selectedSlug === emotion.slug}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
