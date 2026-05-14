import React from 'react';

export function EmotionCard({ emotion, isSelected, onSelect }) {
  return (
    <button
      onClick={() => onSelect(emotion.slug)}
      className={`w-full text-left p-6 rounded-2xl transition-all duration-300 border ${
        isSelected 
          ? 'bg-[#F4F3EF] border-foreground/10 text-foreground' 
          : 'bg-transparent border-foreground/[0.03] text-foreground/50 hover:border-foreground/5 hover:bg-foreground/[0.01]'
      }`}
    >
      <span className="font-serif text-lg tracking-wide">{emotion.name}</span>
    </button>
  );
}

export default function EmotionSelector({ emotions, selectedSlug, onSelect }) {
  return (
    <div className="grid grid-cols-1 gap-3">
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
