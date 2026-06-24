import React, { useState } from 'react';
import { Download, Share2, Copy, Check } from 'lucide-react';
import * as htmlToImage from 'html-to-image';
import { ANALYTICS_EVENTS } from '../../analytics/events';
import { captureEvent } from '../../analytics/posthogClient';
import { captureException } from '../../observability/sentry';
import EditorialActionRow from './EditorialActionRow';

export default function ShareCardActions({ cardRef, shareText, shareUrl, fileName = "capio-fragmento.png" }) {
  const [isExporting, setIsExporting] = useState(false);
  const [manualSaveDataUrl, setManualSaveDataUrl] = useState(null);

  const getExportOptions = () => ({
    pixelRatio: 3,
    backgroundColor: '#F8F7F4',
    style: {
      transform: 'none',
      transition: 'none',
      animation: 'none'
    }
  });



  const handleShare = async () => {
    if (!cardRef.current || isExporting) return;
    localStorage.setItem('capio_engaged_share', 'true');
    captureEvent(ANALYTICS_EVENTS.SHARE_CLICKED, {
      share_type: 'image',
      surface: 'share_card_actions',
    });

    console.log("[CAPIO DEBUG SHARE] handleShare iniciado. Params recebidos no componente:", {
      shareText,
      shareUrl
    });

    try {
      setIsExporting(true);
      const dataUrl = await htmlToImage.toJpeg(cardRef.current, getExportOptions());
      captureEvent(ANALYTICS_EVENTS.SHARE_IMAGE_GENERATED, {
        action: 'native_share',
      });
      
      const res = await fetch(dataUrl);
      const blob = await res.blob();
      const file = new File([blob], fileName.replace('.png', '.jpg'), { type: 'image/jpeg' });

      console.log("[CAPIO DEBUG SHARE] Arquivo gerado para share:", {
        fileName: file.name,
        fileType: file.type,
        fileSize: file.size
      });

      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

      if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
        try {
          const sharePayload = {
            title: 'CAPIO',
            text: shareText,
            url: shareUrl,
            files: [file]
          };
          console.log("[CAPIO DEBUG SHARE] Chamando navigator.share() com o payload:", sharePayload);
          await navigator.share(sharePayload);
          console.log("[CAPIO DEBUG SHARE] navigator.share() sucesso!");
          return;
        } catch (err) {
          if (err.name === 'AbortError') return;
          console.error("[CAPIO DEBUG SHARE] Erro no share nativo:", err);
        }
      }
      
      // Fallback
      if (isMobile) {
        setManualSaveDataUrl(dataUrl);
      } else {
        const link = document.createElement('a');
        link.download = fileName;
        link.href = dataUrl;
        link.click();
      }
    } catch (error) {
      console.error('Erro ao compartilhar imagem:', error);
      captureException(error, { tags: { area: 'share', action: 'image_share' } });
    } finally {
      setIsExporting(false);
    }
  };

  const actions = [
    {
      label: "Compartilhar",
      ariaLabel: "Compartilhar Imagem",
      icon: Share2,
      onClick: handleShare,
      disabled: isExporting
    }
  ];

  return (
    <>
      <EditorialActionRow actions={actions} />
      
      {manualSaveDataUrl && (
        <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/95 px-4 backdrop-blur-sm animate-fade-in">
          <p className="text-white text-center mb-6 font-sans text-[11px] uppercase tracking-widest leading-relaxed max-w-[80%] opacity-90">
            Toque e segure na imagem para salvar na galeria
          </p>
          <img 
            src={manualSaveDataUrl} 
            alt="Toque e segure para salvar" 
            className="max-w-full max-h-[70vh] rounded-lg shadow-2xl object-contain mb-8" 
          />
          <button 
            onClick={() => setManualSaveDataUrl(null)} 
            className="px-6 py-3 border border-white/20 text-white hover:bg-white hover:text-black transition-colors rounded-none font-sans text-[10px] uppercase tracking-widest"
          >
            Fechar
          </button>
        </div>
      )}
    </>
  );
}
