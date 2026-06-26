import React, { useState, useRef } from 'react';
import Card from '../ui/Card';
import ShareButton from '../ui/ShareButton';
import ShareableCard from '../ui/ShareableCard';
import ShareCardActions from '../ui/ShareCardActions';

export default function ReflectionCard({ data }) {
  const [showVerse, setShowVerse] = useState(false);
  const cardRef = useRef(null);
  
  const title = data.title || "Reflexão de hoje";
  const mainContent = data.reflection_body;
  const mainTruth = data.main_truth || data.thread_of_the_word || data.guiding_question;
  const dailyCompanion = data.daily_companion || data.the_word_continues;
  const scriptureReference = data.scripture_reference;
  const scriptureText = data.scripture_text;
  const prayer = data.closing_prayer;

  // Extração de quote dinâmica baseada no próprio corpo da reflexão se ausente do backend
  const getDynamicFallback = (body) => {
    if (!body) return "O silêncio que nos conduz à Palavra.";
    const paragraphs = body.split('\n').map(p => p.trim()).filter(p => p.length > 0);
    if (paragraphs.length === 0) return "O silêncio que nos conduz à Palavra.";
    const firstParagraph = paragraphs[0];
    const sentences = firstParagraph.split(/[.!?]+/g).map(s => s.trim()).filter(s => s.length > 25 && s.length < 120);
    if (sentences.length > 0) {
      return sentences[0] + ".";
    }
    if (firstParagraph.length <= 130) {
      return firstParagraph;
    }
    return firstParagraph.substring(0, 127) + "...";
  };

  const shareQuote = data.share_text || data.share_quote || data.final_fragment || data.highlight || getDynamicFallback(data.reflection_body);

  // Formatação para compartilhamento
  const publicUrl = data.public_id ? `${window.location.origin}/share/reflection/${data.public_id}` : window.location.origin;
  const shareText = `Uma Palavra para hoje.\n\n${title}\n${scriptureReference}\n\n"${scriptureText || ''}"\n\nLer na CAPIO:`;

  return (
    <div className="px-4 md:px-8 pb-12">
      <Card className="space-y-16 pb-24 max-w-4xl mx-auto pt-16">
        {/* 1. A Palavra no topo */}
        {(scriptureReference || scriptureText) && (
          <section className="space-y-6">
            <p className="font-serif text-[11px] text-accent italic tracking-widest text-center">
              {scriptureReference} — NVI
            </p>
            {!showVerse ? (
              <div className="text-center">
                <button 
                  onClick={() => setShowVerse(true)}
                  className="group inline-flex items-center space-x-3 text-[11px] font-serif italic text-accent hover:text-accent/70 transition-colors"
                >
                  <span>Mergulhar na Palavra</span>
                  <span className="text-[8px] transition-transform group-hover:translate-y-1">▼</span>
                </button>
              </div>
            ) : (
              <div className="space-y-4 animate-fade-in-fast max-w-lg mx-auto text-center">
                {scriptureText && (
                  <p className="font-serif italic text-foreground text-xl leading-relaxed">
                    "{scriptureText}"
                  </p>
                )}
              </div>
            )}
          </section>
        )}

        <div className="space-y-24">
          {/* 2. Título como tema emergente */}
          <header className="text-center pt-8">
            <h1 className="font-serif text-2xl text-brand italic leading-tight">
              {title}
            </h1>
          </header>

          {/* 3. Reflexão com Micro-condução */}
          {mainContent && (
            <section className="space-y-8">
              <p className="text-[10px] font-serif italic text-accent text-center tracking-widest">
                Para guardar no coração
              </p>
              <div className="max-w-xl mx-auto">
                <p className="text-contemplative text-foreground/80 whitespace-pre-wrap">
                  {mainContent}
                </p>
              </div>
            </section>
          )}

          {/* 4. O Fio da Palavra */}
          {mainTruth && (
            <section className="space-y-8 max-w-[85%] mx-auto text-center pt-8">
              <p className="text-[10px] font-serif italic text-accent tracking-widest">
                O Fio da Palavra
              </p>
              <p className="font-serif text-lg text-foreground/90 italic leading-relaxed">
                {mainTruth}
              </p>
            </section>
          )}

          {/* 5. A Palavra Continua */}
          {dailyCompanion && (
            <section className="space-y-8 max-w-xl mx-auto text-center pt-8">
              <p className="text-[10px] font-serif italic text-accent tracking-widest">
                A Palavra Continua
              </p>
              <p className="text-contemplative text-foreground/75 leading-relaxed font-serif">
                {dailyCompanion}
              </p>
            </section>
          )}

          {/* 6. Oração */}
          {prayer && (
            <section className="text-center space-y-10 pt-8">
              <div className="w-8 h-px bg-border mx-auto" />
              <div className="space-y-8">
                <p className="text-[10px] font-serif italic text-accent tracking-widest">
                  Fale com Deus no seu silêncio
                </p>
                <p className="font-serif text-base text-foreground/70 italic leading-relaxed max-w-sm mx-auto">
                  {prayer}
                </p>
              </div>
            </section>
          )}

          {/* Assinatura Discreta de Encerramento */}
          <div className="text-center pt-12 pb-4 font-serif italic text-xs text-foreground/45">
            A leitura termina aqui.<br />
            A Palavra continua com você.
          </div>

          {/* 7. Fragmento Final Compartilhável */}
          <section className="space-y-8 pt-16 border-t border-border">
            <ShareableCard 
              ref={cardRef}
              type="reflection"
              quote={shareQuote}
              reference="Reflexão do Dia"
              bgImage={(!data.share_bg_image || data.share_bg_image === "gradient_light") ? "random" : data.share_bg_image}
            />
            <ShareCardActions 
              cardRef={cardRef}
              shareText={`"${shareQuote}"\n\nReflexão do Dia na CAPIO:`}
              shareUrl={publicUrl}
              fileName="capio-reflexao.png"
            />
          </section>

          <div className="flex justify-center pt-16 pb-8">
            <ShareButton 
              title={`Uma Palavra para você`} 
              text={shareText} 
              url={publicUrl}
            />
          </div>
        </div>
      </Card>
    </div>
  );
}
