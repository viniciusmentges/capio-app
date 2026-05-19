import React, { useState, useEffect } from 'react';
import { useWebPush } from '../../hooks/useWebPush';
import { useInstallEligibility } from '../../hooks/useInstallEligibility';
import { usePWA } from '../../hooks/usePWA';
import Button from '../ui/Button';

export default function PushOptInPrompt() {
  const { isSupported, isSubscribed, permission, subscribeUser } = useWebPush();
  const { isEligible: isPWAEligible } = useInstallEligibility();
  const { isInstalled } = usePWA();
  
  const [selectedTime, setSelectedTime] = useState('morning'); // 'morning', 'evening', 'any'
  const [dismissed, setDismissed] = useState(false);

  // Verificar se o convite foi rejeitado recentemente (há menos de 7 dias)
  useEffect(() => {
    const dismissedTimeStr = localStorage.getItem('capio_push_dismissed_time');
    if (dismissedTimeStr) {
      const dismissedTime = parseInt(dismissedTimeStr, 10);
      const sevenDays = 7 * 24 * 60 * 60 * 1000;
      if (Date.now() - dismissedTime < sevenDays) {
        setDismissed(true);
      }
    }
  }, []);

  const handleDismiss = () => {
    localStorage.setItem('capio_push_dismissed_time', Date.now().toString());
    setDismissed(true);
  };

  const handleSubscribe = async () => {
    const success = await subscribeUser(selectedTime);
    if (success) {
      console.log(`Usuário ativou notificações com preferência de horário: ${selectedTime}`);
    }
    setDismissed(true);
  };

  // Regras estritas de elegibilidade da interface:
  // - O dispositivo deve suportar notificações push
  // - O usuário não pode estar inscrito
  // - A permissão não pode estar explicitamente negada (denied)
  // - O prompt não foi recusado nos últimos 7 dias
  // - EVITAR conflito visual: se o prompt de instalação da PWA estiver ativo, ocultar este prompt!
  const isPWAActive = isPWAEligible && !isInstalled;
  
  if (!isSupported || isSubscribed || permission === 'denied' || dismissed || isPWAActive) {
    return null;
  }

  // Garantir também que haja algum engajamento mínimo antes de oferecer lembretes
  const sessionCount = parseInt(localStorage.getItem('capio_session_count') || '1', 10);
  const hasDevotional = localStorage.getItem('capio_devotional_completed') === 'true';
  const hasReflection = localStorage.getItem('capio_reflection_viewed') === 'true';
  
  const hasActivity = hasDevotional || hasReflection;
  const isReturning = sessionCount >= 2;

  if (!isReturning && !hasActivity) {
    return null;
  }

  return (
    <div className="w-full bg-foreground/[0.015] border border-foreground/[0.03] p-8 rounded-sm text-center space-y-6 max-w-md mx-auto my-12 animate-fade-in safe-x">
      <div className="space-y-3">
        <span className="font-serif italic text-[10px] text-foreground/20 tracking-widest uppercase">
          Um chamado silencioso
        </span>
        <h3 className="font-serif text-lg text-foreground/80 leading-tight">
          Deseja receber um lembrete silencioso?
        </h3>
        <p className="font-serif italic text-xs text-foreground/50 leading-relaxed max-w-sm mx-auto">
          A CAPIO enviará apenas um convite discreto no momento escolhido para ajudar a manter sua pausa de oração. Sem pressões ou cobranças.
        </p>
      </div>

      {/* Seletor de Horários Editorial e Premium */}
      <div className="max-w-xs mx-auto py-2">
        <span className="block text-[8px] uppercase tracking-[0.2em] text-foreground/35 mb-3 font-sans">
          Momento preferido para a pausa
        </span>
        <div className="grid grid-cols-3 gap-2 p-1 bg-foreground/[0.02] border border-foreground/[0.04] rounded-sm">
          <button
            onClick={() => setSelectedTime('morning')}
            className={`py-2 text-[9px] font-serif uppercase tracking-[0.1em] transition-all rounded-sm ${
              selectedTime === 'morning'
                ? 'bg-foreground/5 text-foreground/85 shadow-sm'
                : 'text-foreground/35 hover:text-foreground/60'
            }`}
          >
            Manhã
          </button>
          <button
            onClick={() => setSelectedTime('evening')}
            className={`py-2 text-[9px] font-serif uppercase tracking-[0.1em] transition-all rounded-sm ${
              selectedTime === 'evening'
                ? 'bg-foreground/5 text-foreground/85 shadow-sm'
                : 'text-foreground/35 hover:text-foreground/60'
            }`}
          >
            Noite
          </button>
          <button
            onClick={() => setSelectedTime('any')}
            className={`py-2 text-[9px] font-serif uppercase tracking-[0.1em] transition-all rounded-sm ${
              selectedTime === 'any'
                ? 'bg-foreground/5 text-foreground/85 shadow-sm'
                : 'text-foreground/35 hover:text-foreground/60'
            }`}
          >
            Qualquer
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-4 max-w-xs mx-auto pt-1">
        <Button
          onClick={handleSubscribe}
          className="py-3 text-[10px] uppercase tracking-[0.2em] w-full"
        >
          Ativar lembretes
        </Button>
        <button
          onClick={handleDismiss}
          className="text-[9px] uppercase tracking-[0.15em] text-foreground/30 hover:text-foreground/50 transition-colors py-1"
        >
          Agora não
        </button>
      </div>
    </div>
  );
}
