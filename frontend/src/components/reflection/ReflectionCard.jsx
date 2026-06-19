import React, { useState, useRef } from 'react';
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

  const shareQuote = data.share_quote || data.final_fragment || data.highlight || getDynamicFallback(data.reflection_body);

  // Formatação para compartilhamento
  const publicUrl = `${window.location.origin}/share/reflection/${data.id}`;
  const shareText = `Uma Palavra para hoje.\n\n${title}\n${scriptureReference}\n\n"${scriptureText || ''}"\n\nLer na CAPIO:`;

  return (
    <div className="w-full">
      <EditorialCard className="space-y-xl">
        {/* 1. A Palavra no topo */}
      {(scriptureReference || scriptureText) && (
        <section className="space-y-sm">
          <EditorialLabel className="text-center">
            {scriptureReference} — NVI
          </EditorialLabel>
          {!showVerse ? (
            <div className="text-center">
              <button 
                onClick={() => setShowVerse(true)}
                className="group inline-flex items-center space-x-3 editorial-label hover:opacity-70 transition-opacity"
              >
                <span>Mergulhar na Palavra</span>
                <span className="text-[8px] transition-transform group-hover:translate-y-1">↓</span>
              </button>
            </div>
          ) : (
            <div className="space-y-sm animate-fade-in-fast max-w-lg mx-auto text-center">
              {scriptureText && (
                <p className="editorial-title text-xl leading-relaxed opacity-90">
                  "{scriptureText}"
                </p>
              )}
            </div>
          )}
        </section>
      )}

      <div className="space-y-xl">
        {/* 2. Título como tema emergente */}
        <header className="text-center pt-md">
          <EditorialTitle>
            {title}
          </EditorialTitle>
        </header>

        {/* 3. Reflexão com Micro-condução */}
        {mainContent && (
          <section className="space-y-sm">
            <EditorialLabel className="text-center">
              Para guardar no coração
            </EditorialLabel>
            <div className="max-w-xl mx-auto">
              <p className="editorial-body text-center whitespace-pre-wrap">
                {mainContent}
              </p>
            </div>
          </section>
        )}

        {/* 4. Meditação e Oração com Micro-conduções */}
        {(question || prayer) && (
          <div className="space-y-xl pt-lg">
            {question && (
              <section className="space-y-sm max-w-[85%] mx-auto text-center">
                <EditorialLabel>
                  Reflita por um instante
                </EditorialLabel>
                <p className="editorial-title text-lg opacity-80 leading-relaxed">
                  {question}
                </p>
              </section>
            )}

            {prayer && (
              <section className="text-center space-y-md">
                <EditorialDivider variant="short" />
                <div className="space-y-sm">
                  <EditorialLabel>
                    Fale com Deus no seu silêncio
                  </EditorialLabel>
                  <p className="editorial-body opacity-80 italic leading-relaxed max-w-sm mx-auto">
                    {prayer}
                  </p>
                </div>
              </section>
            )}
          </div>
        )}

        {/* 5. Fragmento Final Compartilhável */}
        <EditorialSection className="border-t border-border mt-xl">
          <div className="space-y-sm">
            <ShareableCard 
              ref={cardRef}
              type="reflection"
              quote={shareQuote}
              reference="Reflexão do Dia"
              variant="light"
            />
            <ShareCardActions 
              cardRef={cardRef}
              shareText={`"${shareQuote}"\n\nReflexão do Dia na CAPIO:\n${publicUrl}`}
              fileName="capio-reflexao.png"
            />
          </div>
        </EditorialSection>

        <div className="flex justify-center pb-md">
          <ShareButton 
            title={`Uma Palavra para você`} 
            text={shareText} 
            url={publicUrl}
          />
        </div>
        </div>
      </EditorialCard>
    </div>
  );
}


