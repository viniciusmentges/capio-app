import React, { forwardRef } from 'react';

const ShareableCard = forwardRef(({ type, quote, reference, brandLabel = "CAPIO", variant = "light" }, ref) => {
  const isLight = variant === "light";
  
  return (
    <div className="w-full max-w-[320px] mx-auto aspect-[9/16] relative overflow-hidden rounded-md shadow-sm border border-foreground/5">
      {/* O container interno é o que será efetivamente exportado.
          Não colocamos border-radius nele para que a imagem final exportada (que pode ir para um Story)
          tenha cantos retos. Os cantos arredondados do wrapper são apenas para a visualização no site. */}
      <div 
        ref={ref}
        className={`w-full h-full flex flex-col justify-between p-10 pb-8 pt-10 ${
          isLight 
            ? "bg-gradient-to-b from-[#FCFBF8] to-[#F8F7F4] text-[#4A3B32]" 
            : "bg-gradient-to-b from-[#0F1310] to-[#161D18] text-[#FCFBF8]" 
        }`}
        style={{
          // Forçar estilos inline críticos para a renderização perfeita do html-to-image
          fontFamily: "ui-serif, Georgia, Cambria, 'Times New Roman', Times, serif"
        }}
      >
        {/* Marcador superior minimalista */}
        <div className="flex justify-center mt-2">
           {isLight ? (
             <div className="w-6 h-[0.5px] bg-[#E6E1D8]" />
           ) : (
             <div className="w-6 h-[0.5px] bg-[#7A5C3E]/50" />
           )}
        </div>

        {/* Bloco Central de Meditação */}
        <div className="flex-1 flex flex-col justify-center items-center text-center px-3 space-y-6">
          {type === 'reflection' && (
            <p className={`text-[8px] tracking-[0.25em] uppercase font-sans font-light opacity-50 ${
              isLight ? 'text-[#7A5C3E]/70' : 'text-[#FCFBF8]/50'
            }`}>
              Para guardar no coração
            </p>
          )}
          {type === 'devotional' && (
             <p className={`text-[8px] tracking-[0.25em] uppercase font-sans font-light opacity-50 ${
               isLight ? 'text-[#7A5C3E]/70' : 'text-[#FCFBF8]/50'
             }`}>
              Palavra para o momento
            </p>
          )}
          
          {/* Citação em itálico de altíssimo respiro e elegância */}
          <blockquote className="my-2 max-w-[250px]">
            <p className={`font-serif italic text-lg leading-[1.65] tracking-wide font-normal ${
              isLight ? 'text-[#4A3B32]' : 'text-[#FCFBF8]'
            }`}>
              “{quote}”
            </p>
          </blockquote>
          
          {reference && (
            <p className={`text-[9px] uppercase tracking-[0.2em] font-serif italic opacity-60 pt-3 ${
              isLight ? 'text-[#7A5C3E]/80' : 'text-[#FCFBF8]/80'
            }`}>
              {reference}
            </p>
          )}
        </div>

        {/* Assinatura de Branding Silenciosa da CAPIO */}
        <div className="text-center mb-2 mt-4">
          <p className={`text-[8px] tracking-[0.35em] font-sans font-light uppercase opacity-35 ${
            isLight ? 'text-[#7A5C3E]' : 'text-[#FCFBF8]/55'
          }`}>
            {brandLabel}
          </p>
        </div>
      </div>
    </div>
  );
});

ShareableCard.displayName = 'ShareableCard';

export default ShareableCard;
