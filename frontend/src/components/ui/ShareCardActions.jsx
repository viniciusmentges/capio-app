import React, { useState } from 'react';
import { Download, Share2, Copy, Check } from 'lucide-react';
import * as htmlToImage from 'html-to-image';
import { ANALYTICS_EVENTS } from '../../analytics/events';
import { captureEvent } from '../../analytics/posthogClient';
import { captureException } from '../../observability/sentry';

export default function ShareCardActions({ cardRef, shareText, fileName = "capio-fragmento.png" }) {
  const [isCopied, setIsCopied] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

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
      captureEvent(ANALYTICS_EVENTS.SHARE_IMAGE_GENERATED, {
        action: 'download',
      });
      const link = document.createElement('a');
      link.download = fileName;
      link.href = dataUrl;
      link.click();
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

  return (
    <div className="flex items-center justify-center space-x-6 pt-6">
      <button 
        onClick={handleDownload}
        disabled={isExporting}
        className="flex flex-col items-center space-y-3 group disabled:opacity-50"
        aria-label="Salvar Imagem"
      >
        <div className="w-12 h-12 rounded-full bg-foreground/5 flex items-center justify-center group-hover:bg-foreground/10 transition-colors">
          <Download className="w-4 h-4 text-foreground/60" />
        </div>
        <span className="text-[9px] font-serif uppercase tracking-[0.2em] text-foreground/40 group-hover:text-foreground/60 transition-colors">
          Salvar fragmento
        </span>
      </button>

      <button 
        onClick={handleShare}
        disabled={isExporting}
        className="flex flex-col items-center space-y-3 group disabled:opacity-50"
        aria-label="Compartilhar Imagem"
      >
        <div className="w-12 h-12 rounded-full bg-foreground/5 flex items-center justify-center group-hover:bg-foreground/10 transition-colors">
          <Share2 className="w-4 h-4 text-foreground/60" />
        </div>
        <span className="text-[9px] font-serif uppercase tracking-[0.2em] text-foreground/40 group-hover:text-foreground/60 transition-colors">
          Compartilhar
        </span>
      </button>

      <button 
        onClick={handleCopyText}
        className="flex flex-col items-center space-y-3 group"
        aria-label="Copiar Texto"
      >
        <div className="w-12 h-12 rounded-full bg-foreground/5 flex items-center justify-center group-hover:bg-foreground/10 transition-colors">
          {isCopied ? (
            <Check className="w-4 h-4 text-foreground/60" />
          ) : (
            <Copy className="w-4 h-4 text-foreground/60" />
          )}
        </div>
        <span className="text-[9px] font-serif uppercase tracking-[0.2em] text-foreground/40 group-hover:text-foreground/60 transition-colors">
          Copiar
        </span>
      </button>
    </div>
  );
}
