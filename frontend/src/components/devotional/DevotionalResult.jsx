import React, { useRef } from 'react';
import Card from '../ui/Card';
import ProgressiveReveal from './ProgressiveReveal';
import ShareButton from '../ui/ShareButton';
import ShareableCard from '../ui/ShareableCard';
import ShareCardActions from '../ui/ShareCardActions';

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
  const publicUrl = devotional.public_id ? `${window.location.origin}/share/devotional/${devotional.public_id}` : '';
  const shareText = `Uma Palavra para hoje.\n\n${title}\n${verse}\n\n"${verseText || ''}"\n\nLer na CAPIO:`;

  return (
    <div className="px-4 md:px-8 pb-12">
      <Card className="space-y-24 pb-24 pt-16 max-w-4xl mx-auto">
        {/* 1. A Palavra: Protagonista e Respirada */}
      <div className="px-6 md:px-0 mb-16">
        {verse && (
          <ProgressiveReveal delay={400} duration={1200}>
            <div className="space-y-8">
              <p className="font-serif text-[10px] text-brand italic tracking-widest text-center uppercase">
                {verse}
              </p>
              <div className="relative group px-2">
                <p className="font-serif italic text-foreground text-2xl leading-relaxed text-center max-w-lg mx-auto">
                  {verseText ? `"${displayedVerse}"` : verse}
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
            </div>
          </ProgressiveReveal>
        )}
      </div>

      <div className="space-y-28 px-4 md:px-12 border-t border-border pt-20">
        {/* 2. O Título: Tema que emerge */}
        <ProgressiveReveal delay={1500}>
          <div className="text-center">
            <h2 className="font-serif text-xl text-brand leading-tight italic">
              {title}
            </h2>
          </div>
        </ProgressiveReveal>

        {/* 3. Reflexão: Profundidade Sóbria */}
        {reflection && (
          <ProgressiveReveal delay={2500}>
            <div className="space-y-10">
              <p className="text-[9px] font-serif italic text-accent text-center tracking-[0.2em] uppercase">
                Ecos da Palavra
              </p>
              <div className="max-w-xl mx-auto">
                <p className="text-contemplative text-foreground/80 whitespace-pre-wrap text-center leading-relaxed">
                  {reflection}
                </p>
              </div>
            </div>
          </ProgressiveReveal>
        )}

        {/* 4. Aplicação Prática: O Gesto Humano */}
        {practicalApp && (
          <ProgressiveReveal delay={4000}>
            <div className="max-w-md mx-auto py-12 px-8 rounded-sm space-y-6 border border-border bg-background">
              <p className="text-[9px] font-serif italic text-accent text-center tracking-widest uppercase">
                O convite hoje
              </p>
              <p className="text-sm font-sans font-light text-foreground/80 text-center leading-relaxed italic">
                {practicalApp}
              </p>
            </div>
          </ProgressiveReveal>
        )}

        {/* 5. Pergunta Contemplativa: O Eco Final */}
        {guidingQuestion && (
          <ProgressiveReveal delay={5500}>
            <div className="space-y-8 pt-4">
              <p className="text-[9px] font-serif italic text-accent text-center tracking-[0.2em] uppercase">
                Para o seu silêncio
              </p>
              <h3 className="font-serif italic text-foreground/80 text-lg text-center max-w-sm mx-auto leading-relaxed">
                {guidingQuestion}
              </h3>
            </div>
          </ProgressiveReveal>
        )}

        {/* 6. Oração: Entrega */}
        {prayer && (
          <ProgressiveReveal delay={7500}>
            <div className="pt-16 space-y-12">
              <div className="w-6 h-px bg-border mx-auto" />
              <div className="space-y-10">
                <p className="text-[9px] font-serif italic text-accent text-center tracking-widest uppercase">
                  Oração
                </p>
                <p className="font-serif italic text-foreground/70 text-lg leading-relaxed text-center max-w-sm mx-auto">
                  {prayer}
                </p>
              </div>
            </div>
          </ProgressiveReveal>
        )}
      </div>

      <ProgressiveReveal delay={9000}>
        {/* 7. Fragmento Final Compartilhável */}
        {publicUrl && (
          <section className="space-y-8 pt-16 border-t border-border">
            <ShareableCard 
              ref={cardRef}
              type="devotional"
              quote={devotional.share_text || devotional.share_quote || verseText || verse}
              reference={verse}
              bgImage={devotional.share_bg_image || "gradient_dark"}
            />
            <ShareCardActions 
              cardRef={cardRef}
              shareText={`"${devotional.share_text || devotional.share_quote || verseText || verse}"\n\n${verse}\n\nLer na CAPIO:\n${publicUrl}`}
              fileName="capio-devocional.png"
            />
          </section>
        )}

        {publicUrl && (
          <div className="flex justify-center pt-16 pb-8">
            <ShareButton 
              title={`Uma Palavra para hoje`} 
              text={shareText} 
              url={publicUrl}
            />
          </div>
        )}
      </ProgressiveReveal>


      {/* Finalização suave */}
      <ProgressiveReveal delay={11000}>
        <div className="text-center pt-12">
          <div className="w-1 h-1 bg-border rounded-full mx-auto mb-8" />
          <p className="text-[9px] text-accent font-serif italic tracking-[0.3em] uppercase">
            Paz
          </p>
        </div>
      </ProgressiveReveal>
      </Card>
    </div>
  );
}


