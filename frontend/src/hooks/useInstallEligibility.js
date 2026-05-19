import { useState, useEffect } from 'react';
import { useStandaloneMode } from './useStandaloneMode';

export function useInstallEligibility() {
  const isStandalone = useStandaloneMode();
  const [isEligible, setIsEligible] = useState(false);
  const [isiOS, setIsiOS] = useState(false);

  useEffect(() => {
    // 1. Detectar se é iOS (iPhone, iPad, iPod)
    const userAgent = window.navigator.userAgent.toLowerCase();
    const matchesiOS = /iphone|ipad|ipod/.test(userAgent);
    setIsiOS(matchesiOS);

    // 2. Se já estiver standalone (instalado), nunca elegível
    if (isStandalone) {
      setIsEligible(false);
      return;
    }

    // 3. Se recusado recentemente (há menos de 7 dias)
    const dismissedTimeStr = localStorage.getItem('capio_pwa_dismissed_time');
    if (dismissedTimeStr) {
      const dismissedTime = parseInt(dismissedTimeStr, 10);
      const sevenDays = 7 * 24 * 60 * 60 * 1000;
      if (Date.now() - dismissedTime < sevenDays) {
        setIsEligible(false);
        return;
      }
    }

    // 4. Sessões e Engajamento
    const sessionCount = parseInt(localStorage.getItem('capio_session_count') || '1', 10);
    const hasDevotional = localStorage.getItem('capio_devotional_completed') === 'true';
    const hasReflection = localStorage.getItem('capio_reflection_viewed') === 'true';
    const hasShared = localStorage.getItem('capio_engaged_share') === 'true';

    // Regras de elegibilidade contemplativa:
    // Não pode mostrar imediatamente ao abrir pela primeira vez. 
    // Só mostramos após engajamento real (leitura concluída, devocional ou compartilhamento) ou se for um usuário recorrente (sessão >= 2).
    const hasActivity = hasDevotional || hasReflection || hasShared;
    const isReturning = sessionCount >= 2;

    if (isReturning || hasActivity) {
      setIsEligible(true);
    } else {
      setIsEligible(false);
    }
  }, [isStandalone]);

  // Função para salvar a recusa por 7 dias
  const dismissEligibility = () => {
    localStorage.setItem('capio_pwa_dismissed_time', Date.now().toString());
    setIsEligible(false);
  };

  // Função para salvar instalação bem-sucedida (nunca mais mostrar)
  const markAsInstalled = () => {
    localStorage.setItem('capio_pwa_installed', 'true');
    setIsEligible(false);
  };

  return {
    isEligible,
    isiOS,
    dismissEligibility,
    markAsInstalled,
  };
}
