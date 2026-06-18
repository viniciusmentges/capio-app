import React from 'react';
import Card from '../ui/Card';
import BibleSection from './BibleSection';
import ProgressiveReveal from '../devotional/ProgressiveReveal';
import ShareButton from '../ui/ShareButton';

export default function BibleExplanationCard({ explanation, onNavigate }) {
  const [isVerseExpanded, setIsVerseExpanded] = React.useState(false);

  const reference = explanation.reference_display || "Passagem";
  const verseRequested = explanation.verse_requested;
  const rawVerseText = explanation.scripture_text;
  
  let parsedVerses = [];
  let isStructured = false;
  
  try {
    const parsed = JSON.parse(rawVerseText);
    if (Array.isArray(parsed)) {
      parsedVerses = parsed;
      isStructured = true;
    }
  } catch (e) {
    // É uma string simples do cache antigo
  }

  // Fallback text if not structured
  const verseText = isStructured ? "" : rawVerseText;
  const isLongVerse = verseText && verseText.length > 200;
  const displayedVerse = isLongVerse && !isVerseExpanded 
    ? `${verseText.substring(0, 180)}...` 
    : verseText;

  // Formatação para compartilhamento
  const publicUrl = `${window.location.origin}/share/explanation/${explanation.id}`;
  const shareTextContent = isStructured 
    ? parsedVerses.map(v => `[${v.number}] ${v.text}`).join('\n')
    : verseText;
  const shareText = `Uma Palavra para hoje.\n\n${reference}\n\n"${shareTextContent}"\n\nLer na CAPIO:`;

  return (
    <div className="space-y-24 pb-32 pt-8">
      {/* 1. A Palavra no topo */}
      <div className="px-6 md:px-0 mb-20">
        <ProgressiveReveal delay={400} duration={1200}>
          <div className="space-y-8">
            <div className="text-center space-y-2 mb-12">
              <p className="font-serif text-lg text-foreground/80 tracking-wide">
                {explanation.book_name || reference}
              </p>
              {explanation.chapter && (
                <p className="font-serif text-[10px] text-foreground/45 italic tracking-[0.2em] uppercase">
                  Capítulo {explanation.chapter}
                </p>
              )}
            </div>

            {isStructured ? (
              <div className="relative group px-2 max-w-lg mx-auto space-y-4">
                {parsedVerses.map((verse, index) => {
                  const isHighlighted = verseRequested && String(verse.number) === String(verseRequested);
                  return (
                    <p 
                      key={index} 
                      className={`font-serif leading-relaxed transition-colors duration-500 rounded-sm px-2 py-1 ${
                        isHighlighted 
                          ? "text-foreground/85 bg-[#A68463]/[0.05] border-l-[1.5px] border-[#A68463]/40" 
                          : "text-foreground/85"
                      }`}
                    >
                      <sup className={`text-[9px] mr-2 font-sans tracking-tight ${isHighlighted ? "opacity-70 text-[#A68463]" : "opacity-40"}`}>{verse.number}</sup>
                      {verse.text}
                    </p>
                  );
                })}
                <div className="flex items-center justify-between pt-16">
                  {explanation.prev_chapter && onNavigate ? (
                    <button onClick={() => onNavigate(explanation.prev_chapter)} className="font-serif text-[10px] text-foreground/40 hover:text-foreground/70 transition-colors uppercase tracking-widest">
                      &larr; Capítulo {explanation.prev_chapter.split(" ").pop()}
                    </button>
                  ) : <div className="w-16" />}
                  <div className="w-16" />
                  {explanation.next_chapter && onNavigate ? (
                    <button onClick={() => onNavigate(explanation.next_chapter)} className="font-serif text-[10px] text-foreground/40 hover:text-foreground/70 transition-colors uppercase tracking-widest">
                      Capítulo {explanation.next_chapter.split(" ").pop()} &rarr;
                    </button>
                  ) : <div className="w-16" />}
                </div>
              </div>
            ) : (
              verseText && (
                <div className="relative group px-2">
                  <p className="font-serif italic text-foreground/85 text-2xl leading-relaxed text-center max-w-lg mx-auto">
                    "{displayedVerse}"
                  </p>
                  {isLongVerse && !isVerseExpanded && (
                    <button 
                      onClick={() => setIsVerseExpanded(true)}
                      className="mt-6 mx-auto block text-[10px] font-serif italic text-foreground/50 hover:text-foreground/70 transition-colors uppercase tracking-widest"
                    >
                      continuar leitura ↓
                    </button>
                  )}
                </div>
              )
            )}
          </div>
        </ProgressiveReveal>
      </div>

      <div className="space-y-40 px-6 md:px-0 pt-16">
        <ProgressiveReveal delay={1600}>
          <div className="flex items-center justify-center space-x-6 max-w-md mx-auto mb-16 opacity-60">
            <div className="h-px bg-foreground/10 flex-grow" />
            <p className="font-serif text-[9px] uppercase tracking-[0.2em] text-foreground/60 italic">
              Compreendendo esta passagem
            </p>
            <div className="h-px bg-foreground/10 flex-grow" />
          </div>
        </ProgressiveReveal>

        <ProgressiveReveal delay={1800}>
          <div className="space-y-8">
             <p className="text-[9px] font-serif italic text-foreground/40 text-center tracking-[0.2em] uppercase">
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
              <p className="text-[9px] font-serif italic text-foreground/40 text-center tracking-[0.2em] uppercase">
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
              <p className="text-[9px] font-serif italic text-foreground/45 text-center tracking-widest uppercase">
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
              <p className="text-[9px] font-serif italic text-foreground/40 text-center tracking-[0.2em] uppercase">
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
                <p className="text-[9px] font-serif italic text-foreground/40 text-center tracking-widest uppercase">
                  Oração
                </p>
                <p className="font-serif italic text-foreground/55 text-lg leading-relaxed text-center max-w-sm mx-auto">
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
          <p className="text-[9px] text-foreground/40 font-serif italic tracking-[0.3em] uppercase">
            Luz
          </p>
        </div>
      </ProgressiveReveal>
    </div>
  );
}

