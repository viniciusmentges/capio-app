import React, { useState } from 'react';
import { Download, Share2, Copy, Check } from 'lucide-react';
import * as htmlToImage from 'html-to-image';
import { ANALYTICS_EVENTS } from '../../analytics/events';
import { captureEvent } from '../../analytics/posthogClient';
import { captureException } from '../../observability/sentry';
import EditorialActionRow from './EditorialActionRow';

export default function ShareCardActions({ cardRef, shareText, fileName = "capio-fragmento.png" }) {
  const [isCopied, setIsCopied] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [manualSaveDataUrl, setManualSaveDataUrl] = useState(null);

  const getExportOptions = () => ({
    pixelRatio: 3,
    backgroundColor: null,
    // Remover animações e transições na hora do print
    style: {
      transform: 'none',
      transition: 'none',
      animation: 'none'
    }
  });

  const handleDownload = async () => {
    if (!cardRef.current || isExporting) return;
    localStorage.setItem('capio_engaged_share', 'true');
    try {
      setIsExporting(true);
      const dataUrl = await htmlToImage.toPng(cardRef.current, getExportOptions());
      captureEvent(ANALYTICS_EVENTS.SHARE_IMAGE_GENERATED, { action: 'download' });

      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

      if (isMobile) {
        try {
          const res = await fetch(dataUrl);
          const blob = await res.blob();
          const file = new File([blob], fileName, { type: 'image/png' });

          if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
            await navigator.share({
              files: [file]
            });
            return;
          }
        } catch (err) {
          if (err.name === 'AbortError') return;
          console.error("Erro no share nativo para salvar:", err);
        }

        // Fallback: Mostrar imagem em tela cheia para salvar manualmente
        setManualSaveDataUrl(dataUrl);
      } else {
        // Desktop Fallback
        const link = document.createElement('a');
        link.download = fileName;
        link.href = dataUrl;
        link.click();
      }
    } catch (error) {
      console.error('Erro ao gerar imagem:', error);
      captureException(error, { tags: { area: 'share', action: 'image_download' } });
    } finally {
      setIsExporting(false);
    }
  };

  const handleShare = async () => {
    if (!cardRef.current || isExporting) return;
    localStorage.setItem('capio_engaged_share', 'true');
    captureEvent(ANALYTICS_EVENTS.SHARE_CLICKED, {
      share_type: 'image',
      surface: 'share_card_actions',
    });
    try {
      setIsExporting(true);
      const dataUrl = await htmlToImage.toPng(cardRef.current, getExportOptions());
      captureEvent(ANALYTICS_EVENTS.SHARE_IMAGE_GENERATED, {
        action: 'native_share',
      });
      
      const res = await fetch(dataUrl);
      const blob = await res.blob();
      const file = new File([blob], fileName, { type: 'image/png' });

      if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: 'CAPIO',
          text: shareText,
          files: [file]
        });
      } else {
        handleDownload();
      }
    } catch (error) {
      console.error('Erro ao compartilhar imagem:', error);
      captureException(error, { tags: { area: 'share', action: 'image_share' } });
      handleDownload();
    } finally {
      setIsExporting(false);
    }
  };

  const handleCopyText = async () => {
    localStorage.setItem('capio_engaged_share', 'true');
    captureEvent(ANALYTICS_EVENTS.SHARE_CLICKED, {
      share_type: 'copy_text',
      surface: 'share_card_actions',
    });
    try {
      await navigator.clipboard.writeText(shareText);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (error) {
      console.error('Erro ao copiar texto:', error);
      captureException(error, { tags: { area: 'share', action: 'copy_text' } });
    }
  };

  const actions = [
    {
      label: "Salvar",
      ariaLabel: "Salvar Imagem",
      icon: Download,
      onClick: handleDownload,
      disabled: isExporting
    },
    {
      label: "Compartilhar",
      ariaLabel: "Compartilhar Imagem",
      icon: Share2,
      onClick: handleShare,
      disabled: isExporting
    },
    {
      label: "Copiar",
      ariaLabel: "Copiar Texto",
      icon: isCopied ? Check : Copy,
      onClick: handleCopyText
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
