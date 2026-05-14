import React, { useState } from 'react';
import { Share2, Check } from 'lucide-react';

export default function ShareButton({ title, text, url }) {
  const [copied, setCopied] = useState(false);

  const handleShare = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    const shareUrl = url || window.location.href;
    const fullText = text ? `${text}\n\nLido na CAPIO: ${shareUrl}` : `Lido na CAPIO: ${shareUrl}`;

    const performCopy = async () => {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        try {
          await navigator.clipboard.writeText(fullText);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
          return true;
        } catch (err) {
          console.error('Clipboard API failed', err);
        }
      }
      
      // Fallback manual para contextos não-seguros (HTTP)
      const textArea = document.createElement("textarea");
      textArea.value = fullText;
      textArea.style.position = "fixed";
      textArea.style.left = "-9999px";
      textArea.style.top = "0";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        const successful = document.execCommand('copy');
        if (successful) {
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        }
      } catch (err) {
        console.error('Fallback copy failed', err);
      }
      
      document.body.removeChild(textArea);
    };

    if (navigator.share) {
      try {
        await navigator.share({
          title: title || 'CAPIO',
          text: text,
          url: shareUrl,
        });
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Share failed', err);
          await performCopy();
        }
      }
    } else {
      await performCopy();
    }
  };


  return (
    <button
      onClick={handleShare}
      className="inline-flex items-center justify-center p-2 text-foreground/10 hover:text-foreground/30 transition-colors focus:outline-none"
      aria-label="Compartilhar"
    >
      {copied ? (
        <div className="flex items-center space-x-2">
          <Check size={14} className="opacity-50" />
          <span className="text-[8px] uppercase tracking-[0.2em] font-sans opacity-50">Copiado</span>
        </div>
      ) : (
        <Share2 size={14} />
      )}
    </button>
  );
}
