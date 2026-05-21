import React from 'react';
import { useRegisterSW } from 'virtual:pwa-register/react';
import { captureException } from '../../observability/sentry';

export default function PWAUpdatePrompt() {
  const {
    needRefresh: [needRefresh, setNeedRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegistered(r) {
      // Verificar se há atualizações no service worker em background a cada 1 hora de forma silenciosa
      if (r) {
        setInterval(() => {
          r.update().catch(err => {
            console.log('Erro silencioso ao verificar atualizações de SW:', err);
            captureException(err, { tags: { area: 'service_worker', action: 'update_check' } });
          });
        }, 60 * 60 * 1000);
      }
    },
  });

  if (!needRefresh) {
    return null;
  }

  const handleUpdate = () => {
    updateServiceWorker(true);
  };

  const handleClose = () => {
    setNeedRefresh(false);
  };

  return (
    <div className="fixed bottom-6 left-6 right-6 md:left-auto md:right-6 md:max-w-sm bg-[#F8F7F4] border border-foreground/[0.06] rounded-sm p-5 shadow-lg z-50 animate-fade-in pb-[calc(1.25rem+env(safe-area-inset-bottom,0px))]">
      <div className="space-y-4">
        <div className="space-y-1 text-left">
          <span className="font-serif italic text-[9px] text-foreground/35 tracking-widest uppercase">
            Espaço CAPIO Evolvido
          </span>
          <p className="font-serif italic text-xs text-foreground/75 leading-relaxed">
            Uma nova reflexão ou melhoria está disponível. Deseja atualizar o seu espaço silencioso agora?
          </p>
        </div>
        
        <div className="flex items-center space-x-6 justify-end pt-1">
          <button
            onClick={handleClose}
            className="text-[9px] uppercase tracking-[0.15em] text-foreground/30 hover:text-foreground/50 transition-colors py-1 focus:outline-none"
          >
            Mais tarde
          </button>
          <button
            onClick={handleUpdate}
            className="text-[9px] uppercase tracking-[0.2em] font-sans font-medium text-foreground/80 hover:text-foreground/50 bg-foreground/[0.04] hover:bg-foreground/[0.08] px-4 py-2 rounded-sm transition-all focus:outline-none"
          >
            Atualizar
          </button>
        </div>
      </div>
    </div>
  );
}
