import React, { forwardRef, useState } from 'react';
import { getShareBackground, SHARE_BACKGROUNDS } from '../../utils/shareBackgrounds';

const ShareableCard = forwardRef(({ type, quote, reference, brandLabel = "CAPIO", bgImage: backendBgImage }, ref) => {
  const [imgError, setImgError] = useState(false);
  
  const bgConfig = getShareBackground(backendBgImage);
  const finalConfig = imgError ? SHARE_BACKGROUNDS.gradient_light : bgConfig;

  const isLight = finalConfig.variant === "light";
  const isImage = finalConfig.variant === "image";
  const variant = finalConfig.variant; // 'light', 'dark', 'image'
  
  const textColor = variant === "light" ? "text-[#4A3B32]" : "text-[#FCFBF8]";
  const dividerColor = variant === "light" ? "bg-[#E6E1D8]" : "bg-[#7A5C3E]/50";
  const subtitleColor = variant === "light" ? "text-[#7A5C3E]/70" : "text-[#FCFBF8]/50";
  const referenceColor = variant === "light" ? "text-[#7A5C3E]/80" : "text-[#FCFBF8]/80";
  const brandColor = variant === "light" ? "text-[#7A5C3E]" : "text-[#FCFBF8]/55";
  
  const backgroundClass = isImage 
    ? "bg-[#111111]" // dark base color behind image
    : (isLight ? "bg-gradient-to-b from-[#FCFBF8] to-[#F8F7F4]" : "bg-gradient-to-b from-[#0F1310] to-[#161D18]");
  
  return (
    <div className="w-full max-w-[320px] mx-auto aspect-[9/16] relative overflow-hidden rounded-md shadow-sm border border-foreground/5">
      {/* O container interno é o que será efetivamente exportado. */}
      <div 
        ref={ref}
        className={`w-full h-full flex flex-col justify-between p-10 pb-8 pt-10 relative overflow-hidden ${backgroundClass} ${textColor}`}
        style={{
          fontFamily: "ui-serif, Georgia, Cambria, 'Times New Roman', Times, serif"
        }}
      >
        {isImage && finalConfig.src && (
          <>
            <img 
              src={finalConfig.src} 
              alt="background" 
              className="absolute inset-0 w-full h-full object-cover z-0"
              crossOrigin="anonymous"
              onError={() => setImgError(true)}
            />
            <div className="absolute inset-0 bg-black/40 z-0" />
          </>
        )}

        {/* Marcador superior minimalista */}
        <div className="flex justify-center mt-2 relative z-10">
           <div className={`w-6 h-[0.5px] ${dividerColor}`} />
        </div>

        {/* Bloco Central de Meditação */}
        <div className="flex-1 flex flex-col justify-center items-center text-center px-3 space-y-6 relative z-10">
          {type === 'reflection' && (
            <p className={`text-[8px] tracking-[0.25em] uppercase font-sans font-light ${subtitleColor}`}>
              Para guardar no coração
            </p>
          )}
          {type === 'devotional' && (
             <p className={`text-[8px] tracking-[0.25em] uppercase font-sans font-light ${subtitleColor}`}>
              Palavra para o momento
            </p>
          )}
          
          {/* Citação em itálico de altíssimo respiro e elegância */}
          <blockquote className="my-2 max-w-[250px]">
            <p className={`font-serif italic text-lg leading-[1.65] tracking-wide font-normal ${textColor}`}>
              “{quote}”
            </p>
          </blockquote>
          
          {reference && (
            <p className={`text-[9px] uppercase tracking-[0.2em] font-serif italic pt-3 ${referenceColor}`}>
              {reference}
            </p>
          )}
        </div>

        {/* Assinatura de Branding Silenciosa da CAPIO */}
        <div className="text-center mb-2 mt-4 relative z-10">
          <p className={`text-[8px] tracking-[0.35em] font-sans font-light uppercase ${brandColor}`}>
            {brandLabel}
          </p>
        </div>
      </div>
    </div>
  );
});

ShareableCard.displayName = 'ShareableCard';

export default ShareableCard;
