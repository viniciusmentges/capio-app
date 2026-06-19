import React, { useRef } from 'react';
import ProgressiveReveal from './ProgressiveReveal';
import ShareButton from '../ui/ShareButton';
import ShareableCard from '../ui/ShareableCard';
import ShareCardActions from '../ui/ShareCardActions';
import {
  EditorialCard,
  EditorialLabel,
  EditorialTitle,
  EditorialDivider,
  EditorialSection
} from '../design-system/editorial';

export default function DevotionalResult({ devotional }) {
  const cardRef = useRef(null);
  const [isVerseExpanded, setIsVerseExpanded] = React.useState(false);

  // Parsing resiliente
  const title = devotional.title || "Para seu coração";
  const verse = devotional.verse || devotional.scripture_reference;
  const verseText = devotional.scripture_text;
  const reflection = devotional.reflection || devotional.content || devotional.message;
  const practicalApp = devotional.practical_application;
  const guidingQuestion = devotional.guiding_question;
  const prayer = devotional.prayer;

  const isLongVerse = verseText && verseText.length > 200;
  const displayedVerse = isLongVerse && !isVerseExpanded 
    ? `${verseText.substring(0, 180)}...` 
    : verseText;

  // Formatação para compartilhamento
  const publicUrl = `${window.location.origin}/share/devotional/${devotional.id}`;
  const shareText = `Uma Palavra para hoje.\n\n${title}\n${verse}\n\n"${verseText || ''}"\n\nLer na CAPIO:`;

  return (
    <div className="w-full">
      <EditorialCard className="space-y-xl">
        {/* 1. A Palavra: Protagonista e Respirada */}
      <div className="mb-lg">
        {verse && (
          <ProgressiveReveal delay={400} duration={1200}>
            <div className="space-y-md">
              <EditorialLabel className="text-center text-brand">
                {verse}
              </EditorialLabel>
              <div className="relative group px-2">
                <p className="editorial-title text-2xl leading-relaxed text-center max-w-lg mx-auto">
                  {verseText ? `"${displayedVerse}"` : verse}
                </p>
                {isLongVerse && !isVerseExpanded && (
                  <button 
                    onClick={() => setIsVerseExpanded(true)}
                    className="mt-sm mx-auto block editorial-label hover:opacity-70 transition-opacity"
                  >
                    continuar leitura ↓
                  </button>
                )}
              </div>
            </div>
          </ProgressiveReveal>
        )}
      </div>

      <EditorialSection className="border-t border-border mt-xl pt-xl space-y-xl">
        {/* 2. O Título: Tema que emerge */}
        <ProgressiveReveal delay={1500}>
          <div className="text-center">
            <EditorialTitle className="text-xl">
              {title}
            </EditorialTitle>
          </div>
        </ProgressiveReveal>

        {/* 3. Reflexão: Profundidade Sóbria */}
        {reflection && (
          <ProgressiveReveal delay={2500}>
            <div className="space-y-sm">
              <EditorialLabel className="text-center">
                Ecos da Palavra
              </EditorialLabel>
              <div className="max-w-xl mx-auto">
                <p className="editorial-body text-center whitespace-pre-wrap">
                  {reflection}
                </p>
              </div>
            </div>
          </ProgressiveReveal>
        )}

        {/* 4. Aplicação Prática: O Gesto Humano */}
        {practicalApp && (
          <ProgressiveReveal delay={4000}>
            <div className="max-w-md mx-auto py-lg px-md rounded-sm space-y-md border border-border bg-background">
              <EditorialLabel className="text-center">
                O convite hoje
              </EditorialLabel>
              <p className="editorial-subtitle text-center">
                {practicalApp}
              </p>
            </div>
          </ProgressiveReveal>
        )}

        {/* 5. Pergunta Contemplativa: O Eco Final */}
        {guidingQuestion && (
          <ProgressiveReveal delay={5500}>
            <div className="space-y-sm">
              <EditorialLabel className="text-center">
                Para o seu silêncio
              </EditorialLabel>
              <h3 className="editorial-title text-lg text-center max-w-sm mx-auto opacity-80">
                {guidingQuestion}
              </h3>
            </div>
          </ProgressiveReveal>
        )}

        {/* 6. Oração: Entrega */}
        {prayer && (
          <ProgressiveReveal delay={7500}>
            <div className="pt-xl space-y-md">
              <EditorialDivider variant="short" />
              <div className="space-y-sm">
                <EditorialLabel className="text-center">
                  Oração
                </EditorialLabel>
                <p className="editorial-body text-center max-w-sm mx-auto italic opacity-80">
                  {prayer}
                </p>
              </div>
            </div>
          </ProgressiveReveal>
        )}
      </EditorialSection>

      <ProgressiveReveal delay={9000}>
        {/* 7. Fragmento Final Compartilhável */}
        <EditorialSection className="border-t border-border mt-xl">
          <div className="space-y-sm">
            <ShareableCard 
              ref={cardRef}
              type="devotional"
              quote={verseText || verse}
              reference={verse}
              variant="dark"
            />
            <ShareCardActions 
              cardRef={cardRef}
              shareText={`"${verseText || verse}"\n\n${verse}\n\nLer na CAPIO:\n${publicUrl}`}
              fileName="capio-devocional.png"
            />
          </div>
        </EditorialSection>
      </ProgressiveReveal>

      <ProgressiveReveal delay={10000}>
        <div className="flex justify-center pb-md">
          <ShareButton 
            title={`Uma Palavra para você`} 
            text={shareText} 
            url={publicUrl}
          />
        </div>
      </ProgressiveReveal>


      {/* Finalização suave */}
      <ProgressiveReveal delay={11000}>
        <div className="text-center pt-xl">
          <EditorialDivider variant="dot" />
          <EditorialLabel>
            Paz
          </EditorialLabel>
        </div>
      </ProgressiveReveal>
      </EditorialCard>
    </div>
  );
}


