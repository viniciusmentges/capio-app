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
        className={`w-full h-full flex flex-col justify-between p-8 ${
          isLight 
            ? "bg-[#FDFCF8] text-foreground/80" 
            : "bg-[#1C241D] text-[#FDFCF8]" 
        }`}
        style={{
          // Forçar estilos inline críticos para a renderização do html-to-image
          fontFamily: "ui-serif, Georgia, Cambria, 'Times New Roman', Times, serif"
        }}
      >
        <div className="flex justify-center mt-6">
           {isLight ? (
             <div className="w-4 h-px bg-foreground/20" />
           ) : (
             <div className="w-4 h-px bg-[#D4AF37]/50" />
           )}
        </div>

        <div className="space-y-8 flex-1 flex flex-col justify-center items-center text-center px-2">
          {type === 'reflection' && (
            <p className={`text-[10px] italic tracking-widest uppercase ${isLight ? 'text-foreground/40' : 'text-[#FDFCF8]/50'}`}>
              Para guardar no coração
            </p>
          )}
          {type === 'devotional' && (
             <p className={`text-[10px] italic tracking-widest uppercase ${isLight ? 'text-foreground/40' : 'text-[#FDFCF8]/50'}`}>
              Palavra para o momento
            </p>
          )}
          
          <p className={`italic text-xl leading-[1.6] ${isLight ? 'text-foreground/90' : 'text-[#FDFCF8]'}`}>
            "{quote}"
          </p>
          
          {reference && (
            <p className={`text-[11px] uppercase tracking-[0.2em] pt-6 ${isLight ? 'text-foreground/50' : 'text-[#FDFCF8]/70'}`}>
              {reference}
            </p>
          )}
        </div>

        <div className="text-center mb-6 mt-4">
          <p className={`text-[9px] tracking-[0.3em] uppercase ${isLight ? 'text-foreground/30' : 'text-[#FDFCF8]/40'}`}>
            {brandLabel}
          </p>
        </div>
      </div>
    </div>
  );
});

ShareableCard.displayName = 'ShareableCard';

export default ShareableCard;
