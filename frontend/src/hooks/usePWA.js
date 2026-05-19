import { useState, useEffect } from 'react';

export function usePWA() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // 1. Monitorar estado de conexão nativo do navegador
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // 2. Capturar o evento de prompt diferido de instalação
    const handleBeforeInstallPrompt = (e) => {
      // Impede o navegador de mostrar o pop-up nativo imediatamente
      e.preventDefault();
      // Salva o evento em estado para usarmos contextualizado
      setDeferredPrompt(e);
      console.log('Evento beforeinstallprompt capturado com sucesso.');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // 3. Monitorar a finalização da instalação
    const handleAppInstalled = () => {
      console.log('CAPIO foi guardada na tela de início com sucesso!');
      setDeferredPrompt(null);
      setIsInstalled(true);
    };

    window.addEventListener('appinstalled', handleAppInstalled);

    // Verificar se já está rodando de forma standalone (instalado)
    if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone) {
      setIsInstalled(true);
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Método disparado pelo nosso botão de instalação personalizado
  const triggerInstall = async () => {
    if (!deferredPrompt) {
      console.warn('Nenhum prompt de instalação está disponível.');
      return false;
    }
    
    // Dispara o prompt nativo do navegador
    deferredPrompt.prompt();
    
    // Aguarda a resposta do usuário
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`Usuário respondeu ao convite de instalação: ${outcome}`);
    
    // Limpa o prompt diferido para não usar novamente
    setDeferredPrompt(null);
    return outcome === 'accepted';
  };

  return {
    isOnline,
    isInstalled,
    canInstall: !!deferredPrompt,
    triggerInstall
  };
}
