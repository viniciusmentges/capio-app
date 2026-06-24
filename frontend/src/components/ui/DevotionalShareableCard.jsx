import React, { forwardRef, useState } from 'react';
import { getShareDevotionalBackground } from '../../utils/shareDevotionalBackgrounds';

const DevotionalShareableCard = forwardRef(({ quote, reference, bgImage }, ref) => {
  const [imgError, setImgError] = useState(false);
  
  // O componente Devocional sempre usa imagens fotográficas, então a cor do texto é clara com sombra suave.
  const bgUrl = getShareDevotionalBackground(bgImage);
  
  return (
    <div className="w-full max-w-[320px] mx-auto aspect-[9/16] relative overflow-hidden rounded-none">
      {/* O container interno é o que será efetivamente exportado. Fundo F8F7F4 garante base sólida para o JPEG. */}
      <div 
        ref={ref}
        className="w-full h-full flex flex-col justify-center p-8 pb-10 pt-10 relative overflow-hidden bg-[#F8F7F4] text-[#FCFBF8]"
        style={{
          fontFamily: "ui-serif, Georgia, Cambria, 'Times New Roman', Times, serif"
        }}
      >
        {!imgError && bgUrl && (
          <>
            <img 
              src={bgUrl} 
              alt="background" 
              className="absolute inset-0 w-full h-full object-cover z-0"
              onError={() => setImgError(true)}
            />
            {/* Overlay sutil para garantir leitura do texto branco em fotos claras */}
            <div className="absolute inset-0 bg-black/30 z-0" />
          </>
        )}

        {/* Conteúdo Principal (Centralizado) */}
        <div className="flex-1 flex flex-col justify-center items-center z-10 space-y-6">
          <p className="text-xl md:text-2xl leading-relaxed italic text-center text-[#FCFBF8] drop-shadow-md px-2 whitespace-pre-wrap">
            {quote}
          </p>
          
          {reference && (
            <p className="text-sm font-sans tracking-widest text-[#FCFBF8]/80 drop-shadow-sm uppercase">
              {reference}
            </p>
          )}
        </div>
        
        {/* Assinatura (Logo da CAPIO discreta) */}
        <div className="flex justify-center z-10 mt-8">
           <span className="font-sans text-[10px] tracking-[0.3em] font-semibold text-[#FCFBF8]/60 drop-shadow-sm uppercase">
             CAPIO
           </span>
        </div>
      </div>
    </div>
  );
});

DevotionalShareableCard.displayName = "DevotionalShareableCard";

export default DevotionalShareableCard;
