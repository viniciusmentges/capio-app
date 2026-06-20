import React from 'react';
import Card from '../ui/Card';
import EditorialLabel from '../ui/EditorialLabel';
import EditorialDivider from '../ui/EditorialDivider';
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
    <div className="px-4 md:px-8 pb-12">
      <Card className="space-y-24 pb-24 pt-16 max-w-4xl mx-auto">
        {/* 1. A Palavra no topo */}
      <div className="px-6 md:px-0 mb-20">
        <ProgressiveReveal delay={400} duration={1200}>
          <div className="space-y-8">
            <div className="text-center space-y-2 mb-12">
              <p className="font-serif text-lg text-brand tracking-wide">
                {explanation.book_name || reference}
              </p>
              {explanation.chapter && (
                <p className="font-serif text-[10px] text-accent italic tracking-[0.2em] uppercase">
                  Capítulo {explanation.chapter}
                </p>
              )}
            </div>

            {isStructured ? (
              <div className="relative group px-2 max-w-lg mx-auto space-y-4">
                {parsedVerses.map((verse, index) => {
                  let isHighlighted = false;
                  if (verseRequested) {
                    const reqStr = String(verseRequested);
                    if (reqStr.includes('-')) {
                      const [start, end] = reqStr.split('-').map(Number);
                      const current = Number(verse.number);
                      if (!isNaN(start) && !isNaN(end) && current >= start && current <= end) {
                        isHighlighted = true;
                      }
                    } else if (reqStr === String(verse.number)) {
                      isHighlighted = true;
                    }
                  }
                  
                  return (
                    <p 
                      key={index} 
                      className={`font-serif text-bible transition-colors duration-500 rounded-sm px-2 py-1 ${
                        isHighlighted 
                          ? "text-foreground bg-accent/[0.05] border-l-[1.5px] border-accent/40" 
                          : "text-foreground/90"
                      }`}
                    >
                      <sup className={`text-[9px] mr-2 font-sans tracking-tight ${isHighlighted ? "opacity-70 text-accent" : "opacity-40"}`}>{verse.number}</sup>
                      {verse.text}
                    </p>
                  );
                })}
                <div className="flex items-center justify-between pt-16">
                  {explanation.prev_chapter && onNavigate ? (
                    <button onClick={() => onNavigate(explanation.prev_chapter)} className="font-serif text-[10px] text-accent hover:opacity-70 transition-opacity uppercase tracking-widest">
                      &larr; Capítulo {explanation.prev_chapter.split(" ").pop()}
                    </button>
                  ) : <div className="w-16" />}
                  <div className="w-16" />
                  {explanation.next_chapter && onNavigate ? (
                    <button onClick={() => onNavigate(explanation.next_chapter)} className="font-serif text-[10px] text-accent hover:opacity-70 transition-opacity uppercase tracking-widest">
                      Capítulo {explanation.next_chapter.split(" ").pop()} &rarr;
                    </button>
                  ) : <div className="w-16" />}
                </div>
              </div>
            ) : (
              verseText && (
                <div className="relative group px-2">
                  <p className="font-serif italic text-foreground text-bible text-center max-w-lg mx-auto">
                    "{displayedVerse}"
                  </p>
                  {isLongVerse && !isVerseExpanded && (
                    <button 
                      onClick={() => setIsVerseExpanded(true)}
                      className="mt-6 mx-auto block text-[10px] font-serif italic text-brand hover:text-brand/70 transition-colors uppercase tracking-widest"
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

      <div className="space-y-40 px-4 md:px-12 border-t border-border pt-16">
        <ProgressiveReveal delay={1600}>
          <EditorialDivider variant="content" className="max-w-md mx-auto mb-16">
            <EditorialLabel>
              Compreendendo esta passagem
            </EditorialLabel>
          </EditorialDivider>
        </ProgressiveReveal>

        {explanation.reading_focus_content && (
          <ProgressiveReveal delay={1700}>
            <div className="max-w-md mx-auto mb-16 py-12 px-8 rounded-sm space-y-6 border border-border bg-surface">
              <EditorialLabel className="text-brand">
                {explanation.reading_focus_title || "O foco desta leitura"}
              </EditorialLabel>
              <p className="text-sm font-sans font-light text-foreground/80 text-center leading-relaxed italic">
                {explanation.reading_focus_content}
              </p>
            </div>
          </ProgressiveReveal>
        )}

        <ProgressiveReveal delay={1800}>
          <div className="space-y-8">
             <EditorialLabel>
                O coração do texto
              </EditorialLabel>
            <div className="max-w-xl mx-auto">
              <p className="text-contemplative text-foreground/80 text-center leading-relaxed">
                {explanation.simple_explanation}
              </p>
            </div>
          </div>
        </ProgressiveReveal>

        <div className="space-y-32">
          <ProgressiveReveal delay={3500}>
            <div className="space-y-8">
              <EditorialLabel>
                Contexto
              </EditorialLabel>
              <div className="max-w-xl mx-auto">
                <p className="text-sm font-sans font-light text-foreground/80 text-center leading-relaxed">
                  {explanation.biblical_context}
                </p>
              </div>
            </div>
          </ProgressiveReveal>

          <ProgressiveReveal delay={5500}>
            <div className="max-w-md mx-auto py-12 px-8 rounded-sm space-y-6 border border-border bg-background">
              <EditorialLabel>
                Eco na vida
              </EditorialLabel>
              <p className="text-sm font-sans font-light text-foreground/80 text-center leading-relaxed italic">
                {explanation.practical_application}
              </p>
            </div>
          </ProgressiveReveal>
        </div>

        <ProgressiveReveal delay={7500}>
           <div className="space-y-8">
              <EditorialLabel>
                Reflexão Espiritual
              </EditorialLabel>
              <div className="max-w-xl mx-auto">
                <p className="text-contemplative text-foreground/80 text-center leading-relaxed italic">
                  {explanation.spiritual_reflection}
                </p>
              </div>
            </div>
        </ProgressiveReveal>

        {explanation.optional_prayer && (
          <ProgressiveReveal delay={9500}>
            <div className="pt-16 space-y-12">
              <EditorialDivider />
              <div className="space-y-10">
                <EditorialLabel>
                  Oração
                </EditorialLabel>
                <p className="font-serif italic text-foreground/70 text-lg leading-relaxed text-center max-w-sm mx-auto">
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
          <EditorialDivider variant="dot" className="mb-8" />
          <p className="text-[9px] text-accent font-serif italic tracking-[0.3em] uppercase">
            Luz
          </p>
        </div>
      </ProgressiveReveal>
      </Card>
    </div>
  );
}

