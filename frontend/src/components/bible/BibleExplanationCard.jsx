import React from 'react';
import ProgressiveReveal from '../devotional/ProgressiveReveal';
import ShareButton from '../ui/ShareButton';
import {
  EditorialCard,
  EditorialLabel,
  EditorialTitle,
  EditorialDivider,
  EditorialNavigation,
  EditorialSection
} from '../design-system/editorial';

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
    <div className="w-full">
      <EditorialCard className="space-y-xl">
        {/* 1. A Palavra no topo */}
      <div className="mb-lg">
        <ProgressiveReveal delay={400} duration={1200}>
          <div className="space-y-md">
            <div className="text-center space-y-xs mb-lg">
              <EditorialTitle as="p">
                {explanation.book_name || reference}
              </EditorialTitle>
              {explanation.chapter && (
                <EditorialLabel>
                  Capítulo {explanation.chapter}
                </EditorialLabel>
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
                      className={`editorial-body text-bible transition-colors duration-500 rounded-sm px-2 py-1 ${
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
                <EditorialNavigation 
                    prevTitle={explanation.prev_chapter ? `Capítulo ${explanation.prev_chapter.split(" ").pop()}` : null}
                    onPrev={explanation.prev_chapter && onNavigate ? () => onNavigate(explanation.prev_chapter) : null}
                    nextTitle={explanation.next_chapter ? `Capítulo ${explanation.next_chapter.split(" ").pop()}` : null}
                    onNext={explanation.next_chapter && onNavigate ? () => onNavigate(explanation.next_chapter) : null}
                    className="mt-md"
                  />
              </div>
            ) : (
              verseText && (
                <>
                  <p className="editorial-body text-bible text-center max-w-lg mx-auto italic">
                    "{displayedVerse}"
                  </p>
                  {isLongVerse && !isVerseExpanded && (
                    <button 
                      onClick={() => setIsVerseExpanded(true)}
                      className="mt-sm mx-auto block editorial-label hover:opacity-70 transition-opacity"
                    >
                      continuar leitura ↓
                    </button>
                  )}
                </>
              )
            )}
          </div>
        </ProgressiveReveal>
      </div>

      <EditorialSection className="border-t border-border mt-xl pt-xl space-y-xl">
        <ProgressiveReveal delay={1600}>
          <div className="flex items-center justify-center space-x-4 max-w-md mx-auto mb-lg opacity-60">
            <div className="h-px bg-border flex-grow" />
            <EditorialLabel>
              Compreendendo esta passagem
            </EditorialLabel>
            <div className="h-px bg-border flex-grow" />
          </div>
        </ProgressiveReveal>

        {explanation.reading_focus_content && (
          <ProgressiveReveal delay={1700}>
            <div className="max-w-md mx-auto mb-lg py-lg px-md rounded-sm space-y-md border border-border bg-surface">
              <EditorialLabel className="text-center text-brand">
                {explanation.reading_focus_title || "O foco desta leitura"}
              </EditorialLabel>
              <p className="editorial-subtitle text-center">
                {explanation.reading_focus_content}
              </p>
            </div>
          </ProgressiveReveal>
        )}

        <ProgressiveReveal delay={1800}>
          <div className="space-y-sm">
             <EditorialLabel className="text-center">
                O coração do texto
              </EditorialLabel>
            <div className="max-w-xl mx-auto">
              <p className="editorial-body text-center">
                {explanation.simple_explanation}
              </p>
            </div>
          </div>
        </ProgressiveReveal>

        <div className="space-y-xl">
          <ProgressiveReveal delay={3500}>
            <div className="space-y-sm">
              <EditorialLabel className="text-center">
                Contexto
              </EditorialLabel>
              <div className="max-w-xl mx-auto">
                <p className="editorial-body text-center">
                  {explanation.biblical_context}
                </p>
              </div>
            </div>
          </ProgressiveReveal>

          <ProgressiveReveal delay={5500}>
            <div className="max-w-md mx-auto py-lg px-md rounded-sm space-y-md border border-border bg-background">
              <EditorialLabel className="text-center">
                Eco na vida
              </EditorialLabel>
              <p className="editorial-subtitle text-center">
                {explanation.practical_application}
              </p>
            </div>
          </ProgressiveReveal>
        </div>

        <ProgressiveReveal delay={7500}>
           <div className="space-y-sm">
              <EditorialLabel className="text-center">
                Reflexão Espiritual
              </EditorialLabel>
              <div className="max-w-xl mx-auto">
                <p className="editorial-body text-center italic">
                  {explanation.spiritual_reflection}
                </p>
              </div>
            </div>
        </ProgressiveReveal>

        {explanation.optional_prayer && (
          <ProgressiveReveal delay={9500}>
            <div className="pt-xl space-y-md">
              <EditorialDivider variant="short" />
              <div className="space-y-sm">
                <EditorialLabel className="text-center">
                  Oração
                </EditorialLabel>
                <p className="editorial-body text-center max-w-sm mx-auto italic opacity-80">
                  {explanation.optional_prayer}
                </p>
              </div>
            </div>
          </ProgressiveReveal>
        )}
      </EditorialSection>

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
        <div className="text-center pt-xl">
          <EditorialDivider variant="dot" />
          <EditorialLabel>
            Luz
          </EditorialLabel>
        </div>
      </ProgressiveReveal>
      </EditorialCard>
    </div>
  );
}

