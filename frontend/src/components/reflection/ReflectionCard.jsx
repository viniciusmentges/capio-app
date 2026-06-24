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
  const question = data.guiding_question;
  const scriptureReference = data.scripture_reference;
  const scriptureText = data.scripture_text;
  const prayer = data.closing_prayer;

  // Logs temporários para auditoria de campos recebidos da API
  console.log("[CAPIO AUDIT] Dados de Compartilhamento recebidos:", {
    id: data.id,
    share_quote: data.share_quote,
    final_fragment: data.final_fragment,
    highlight: data.highlight
  });

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

        {/* 4. Meditação e Oração com Micro-conduções */}
        {(question || prayer) && (
          <div className="space-y-24 pt-16">
            {question && (
              <section className="space-y-8 max-w-[85%] mx-auto text-center">
                <p className="text-[10px] font-serif italic text-accent tracking-widest">
                  Reflita por um instante
                </p>
                <p className="font-serif text-lg text-foreground/80 italic leading-relaxed">
                  {question}
                </p>
              </section>
            )}

            {prayer && (
              <section className="text-center space-y-10">
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
          </div>
        )}

        {/* 5. Fragmento Final Compartilhável */}
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
            shareText={`"${shareQuote}"\n\nReflexão do Dia na CAPIO:\n${publicUrl}`}
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
