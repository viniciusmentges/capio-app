import React from 'react';
import Card from '../ui/Card';
import BibleSection from './BibleSection';
import ProgressiveReveal from '../devotional/ProgressiveReveal';
import ShareButton from '../ui/ShareButton';

export default function BibleExplanationCard({ explanation }) {
  const [isVerseExpanded, setIsVerseExpanded] = React.useState(false);

  const reference = explanation.reference_display || "Passagem";
  const verseText = explanation.scripture_text;
  
  const isLongVerse = verseText && verseText.length > 200;
  const displayedVerse = isLongVerse && !isVerseExpanded 
    ? `${verseText.substring(0, 180)}...` 
    : verseText;

  // Formatação para compartilhamento
  const publicUrl = `${window.location.origin}/share/explanation/${explanation.id}`;
  const shareText = `Uma Palavra para hoje.\n\n${reference}\n\n"${verseText}"\n\nLer na CAPIO:`;

  return (
    <div className="space-y-24 pb-32 pt-8">
      {/* 1. A Palavra no topo */}
      <div className="px-6 md:px-0 mb-20">
        <ProgressiveReveal delay={400} duration={1200}>
          <div className="space-y-8">
            <p className="font-serif text-[10px] text-foreground/20 italic tracking-[0.2em] text-center uppercase">
              {reference}
            </p>
            {verseText && (
              <div className="relative group px-2">
                <p className="font-serif italic text-foreground/85 text-2xl leading-relaxed text-center max-w-lg mx-auto">
                  "{displayedVerse}"
                </p>
                {isLongVerse && !isVerseExpanded && (
                  <button 
                    onClick={() => setIsVerseExpanded(true)}
                    className="mt-6 mx-auto block text-[10px] font-serif italic text-foreground/30 hover:text-foreground/50 transition-colors uppercase tracking-widest"
                  >
                    continuar leitura ↓
                  </button>
                )}
              </div>
            )}
          </div>
        </ProgressiveReveal>
      </div>

      <div className="space-y-40 px-6 md:px-0 border-t border-foreground/[0.03] pt-24">
        <ProgressiveReveal delay={1800}>
          <div className="space-y-8">
             <p className="text-[9px] font-serif italic text-foreground/15 text-center tracking-[0.2em] uppercase">
                O coração do texto
              </p>
            <div className="max-w-xl mx-auto">
              <p className="text-contemplative text-foreground/75 text-center leading-relaxed">
                {explanation.simple_explanation}
              </p>
            </div>
          </div>
        </ProgressiveReveal>

        <div className="space-y-32">
          <ProgressiveReveal delay={3500}>
            <div className="space-y-8">
              <p className="text-[9px] font-serif italic text-foreground/15 text-center tracking-[0.2em] uppercase">
                Contexto
              </p>
              <div className="max-w-xl mx-auto">
                <p className="text-sm font-sans font-light text-foreground/60 text-center leading-relaxed">
                  {explanation.biblical_context}
                </p>
              </div>
            </div>
          </ProgressiveReveal>

          <ProgressiveReveal delay={5500}>
            <div className="max-w-md mx-auto bg-foreground/[0.02] py-12 px-8 rounded-sm space-y-6">
              <p className="text-[9px] font-serif italic text-foreground/20 text-center tracking-widest uppercase">
                Eco na vida
              </p>
              <p className="text-sm font-sans font-light text-foreground/60 text-center leading-relaxed italic">
                {explanation.practical_application}
              </p>
            </div>
          </ProgressiveReveal>
        </div>

        <ProgressiveReveal delay={7500}>
           <div className="space-y-8">
              <p className="text-[9px] font-serif italic text-foreground/15 text-center tracking-[0.2em] uppercase">
                Reflexão Espiritual
              </p>
              <div className="max-w-xl mx-auto">
                <p className="text-contemplative text-foreground/75 text-center leading-relaxed italic">
                  {explanation.spiritual_reflection}
                </p>
              </div>
            </div>
        </ProgressiveReveal>

        {explanation.optional_prayer && (
          <ProgressiveReveal delay={9500}>
            <div className="pt-16 space-y-12">
              <div className="w-6 h-px bg-foreground/10 mx-auto" />
              <div className="space-y-10">
                <p className="text-[9px] font-serif italic text-foreground/15 text-center tracking-widest uppercase">
                  Oração
                </p>
                <p className="font-serif italic text-foreground/40 text-lg leading-relaxed text-center max-w-sm mx-auto">
                  {explanation.optional_prayer}
                </p>
              </div>
            </div>
          </ProgressiveReveal>
        )}
      </div>

      <ProgressiveReveal delay={11000}>
        <div className="flex justify-center pt-8">
          <ShareButton 
            title={`Uma Palavra para você`} 
            text={shareText} 
            url={publicUrl}
          />
        </div>
      </ProgressiveReveal>


      <ProgressiveReveal delay={12000}>
        <div className="text-center pt-12">
          <div className="w-1 h-1 bg-foreground/10 rounded-full mx-auto mb-8" />
          <p className="text-[9px] text-foreground/15 font-serif italic tracking-[0.3em] uppercase">
            Luz
          </p>
        </div>
      </ProgressiveReveal>
    </div>
  );
}

