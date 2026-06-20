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

  return <EditorialActionRow actions={actions} />;
}
