import React from 'react';
import { usePWA } from '../../hooks/usePWA';
import { useInstallEligibility } from '../../hooks/useInstallEligibility';
import Button from '../ui/Button';
import { ANALYTICS_EVENTS } from '../../analytics/events';
import { captureEvent } from '../../analytics/posthogClient';

export default function PWAInstallPrompt() {
  const { canInstall, isInstalled, triggerInstall } = usePWA();
  const { isEligible, isiOS, dismissEligibility, markAsInstalled } = useInstallEligibility();
  const shouldShowPrompt = isEligible && !isInstalled && (isiOS || canInstall);

  React.useEffect(() => {
    if (!shouldShowPrompt) return;

    captureEvent(ANALYTICS_EVENTS.PWA_INSTALL_PROMPT_SHOWN, {
      platform: isiOS ? 'ios' : 'browser_prompt',
    });
  }, [isiOS, shouldShowPrompt]);

  // Condições de exibição estritas:
  // - O usuário precisa ser elegível (ter engajamento ou retorno e não ter recusado nos últimos 7 dias)
  // - O aplicativo não pode estar instalado (standalone)
  // - Deve ser iOS Safari OU possuir suporte para instalação diferida (canInstall) no Android/Chrome
  if (!isEligible || isInstalled) {
    return null;
  }

  // Se não for iOS e o navegador não possuir suporte para prompt de instalação (ex: desktop comum ou outro browser incompatível)
  if (!isiOS && !canInstall) {
    return null;
  }

  const handleInstall = async () => {
    if (isiOS) {
      // No iOS, orientamos o usuário manualmente. Não há chamada triggerInstall.
      return;
    }

    const accepted = await triggerInstall();
    if (accepted) {
      markAsInstalled();
    } else {
      dismissEligibility();
    }
  };

  const handleDismiss = () => {
    dismissEligibility();
  };

  return (
    <div className="w-full bg-foreground/[0.015] border border-foreground/[0.03] p-8 rounded-sm text-center space-y-6 max-w-md mx-auto my-12 animate-fade-in safe-x">
      <div className="space-y-3">
        <span className="font-serif italic text-[10px] text-foreground/20 tracking-widest uppercase">
          Um espaço dedicado
        </span>
        <h3 className="font-serif text-lg text-foreground/80 leading-tight">
          Guarde este espaço
        </h3>
        
        {isiOS ? (
          <p className="font-serif italic text-xs text-foreground/50 leading-relaxed max-w-sm mx-auto">
            Para guardar a CAPIO no iPhone, toque no botão de <span className="font-sans font-medium text-foreground/75">Compartilhar</span> na barra do Safari e escolha <span className="font-sans font-medium text-foreground/75">Adicionar à Tela de Início</span>.
          </p>
        ) : (
          <p className="font-serif italic text-xs text-foreground/50 leading-relaxed max-w-sm mx-auto">
            A CAPIO pode ficar na sua tela inicial como um pequeno lugar de oração para o seu dia.
          </p>
        )}
      </div>

      <div className="flex flex-col gap-4 max-w-xs mx-auto pt-2">
        {!isiOS ? (
          <Button
            onClick={handleInstall}
            className="py-3 text-[10px] uppercase tracking-[0.2em] w-full"
          >
            Guardar no celular
          </Button>
        ) : null}
        
        <button
          onClick={handleDismiss}
          className="text-[9px] uppercase tracking-[0.15em] text-foreground/30 hover:text-foreground/50 transition-colors py-1"
        >
          {isiOS ? 'Entendido' : 'Agora não'}
        </button>
      </div>
    </div>
  );
}
