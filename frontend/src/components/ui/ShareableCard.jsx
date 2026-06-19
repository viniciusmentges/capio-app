import React, { forwardRef } from 'react';

const ShareableCard = forwardRef(({ type, quote, reference, brandLabel = "CAPIO", variant = "light" }, ref) => {
  const isLight = variant === "light";
  
  return (
    <div className="w-full max-w-[320px] mx-auto aspect-[9/16] relative overflow-hidden rounded-md shadow-sm border border-border">
      {/* O container interno é o que será efetivamente exportado.
          Não colocamos border-radius nele para que a imagem final exportada (que pode ir para um Story)
          tenha cantos retos. Os cantos arredondados do wrapper são apenas para a visualização no site. */}
      <div 
        ref={ref}
        className={`w-full h-full flex flex-col justify-between p-10 pb-8 pt-10 ${
          isLight 
            ? "bg-background text-foreground" 
            : "bg-foreground text-background" 
        }`}
        style={{
          // Forçar estilos inline críticos para a renderização perfeita do html-to-image
          fontFamily: "ui-serif, Georgia, Cambria, 'Times New Roman', Times, serif"
        }}
      >
        {/* Marcador superior minimalista */}
        <div className="flex justify-center mt-xs">
           <div className={`w-6 h-[0.5px] ${isLight ? 'bg-border' : 'bg-background/20'}`} />
        </div>

        {/* Bloco Central de Meditação */}
        <div className="flex-1 flex flex-col justify-center items-center text-center px-3 space-y-md">
          {type === 'reflection' && (
            <p className="editorial-label opacity-50">
              Para guardar no coração
            </p>
          )}
          {type === 'devotional' && (
             <p className="editorial-label opacity-50">
              Palavra para o momento
            </p>
          )}
          
          {/* Citação em itálico de altíssimo respiro e elegância */}
          <blockquote className="my-sm max-w-[250px]">
            <p className="editorial-title text-lg leading-[1.65] tracking-wide font-normal">
              “{quote}”
            </p>
          </blockquote>
          
          {reference && (
            <p className="editorial-label opacity-60 pt-xs">
              {reference}
            </p>
          )}
        </div>

        {/* Assinatura de Branding Silenciosa da CAPIO */}
        <div className="text-center mb-xs mt-sm">
          <p className="editorial-label opacity-35">
            {brandLabel}
          </p>
        </div>
      </div>
    </div>
  );
});

ShareableCard.displayName = 'ShareableCard';

export default ShareableCard;
