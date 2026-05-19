import { useState, useEffect } from 'react';
import axios from 'axios';

// Chave Pública VAPID padrão para subscrição nativa (substituível conforme necessidade de produção)
const DEFAULT_VAPID_PUBLIC_KEY = 'BI6XF_Rk7wN6dYn0l4V_lP6W9zM1zNf0H7vGzE1uYvT4p4h8i3k8i9u9x9f8e7d6c5b4a3_VAPID_DEFAULT_KEY_CAPIO';

// Conversor auxiliar regulamentar de base64 para Uint8Array exigido pelo navegador
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function useWebPush() {
  const [permission, setPermission] = useState('default');
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [preferredTime, setPreferredTime] = useState('morning');

  // 1. Verificar estado atual da inscrição no carregamento do hook
  useEffect(() => {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      setPermission(Notification.permission);
      
      navigator.serviceWorker.ready
        .then((registration) => {
          return registration.pushManager.getSubscription();
        })
        .then((subscription) => {
          setIsSubscribed(!!subscription);
          setLoading(false);
        })
        .catch((err) => {
          console.error('Erro ao auditar assinatura Web Push no Service Worker:', err);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  // 2. Efetuar a inscrição progressiva e mandar as credenciais para o Django com preferências
  const subscribeUser = async (chosenTime = 'morning') => {
    if (!('Notification' in window) || !('serviceWorker' in navigator)) {
      console.warn('Notificações Push não são suportadas neste dispositivo/navegador.');
      return false;
    }

    try {
      setLoading(true);

      // Solicitar permissão nativa
      const outcome = await Notification.requestPermission();
      setPermission(outcome);

      if (outcome !== 'granted') {
        console.log('Permissão de notificações negada pelo usuário.');
        setLoading(false);
        return false;
      }

      // Preparar chaves VAPID
      const registration = await navigator.serviceWorker.ready;
      const vapidPublicKey = import.meta.env.VITE_VAPID_PUBLIC_KEY || DEFAULT_VAPID_PUBLIC_KEY;
      const convertedKey = urlBase64ToUint8Array(vapidPublicKey);

      // Efetuar registro no navegador
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedKey,
      });

      // Serializar credenciais para o backend Django
      const subJSON = subscription.toJSON();
      
      // Metadados do dispositivo do usuário
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'America/Sao_Paulo';
      const userAgent = navigator.userAgent;
      const platform = navigator.platform || '';

      const payload = {
        endpoint: subJSON.endpoint,
        p256dh: subJSON.keys.p256dh,
        auth: subJSON.keys.auth,
        user_agent: userAgent,
        platform: platform,
        timezone: timezone,
        preferred_time: chosenTime,
        enabled: true
      };

      // Configurar requisição autenticada caso haja token JWT
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      // Enviar ao backend Django
      await axios.post(`${apiUrl}/api/auth/push/subscribe/`, payload, { headers });

      setIsSubscribed(true);
      setPreferredTime(chosenTime);
      console.log('Assinatura de Web Push persistida no Django com sucesso!');
      setLoading(false);
      return true;
    } catch (err) {
      console.error('Falha ao registrar assinatura Web Push:', err);
      setLoading(false);
      return false;
    }
  };

  // 3. Cancelar a assinatura de notificações notificando o backend
  const unsubscribeUser = async () => {
    try {
      setLoading(true);
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (subscription) {
        const subJSON = subscription.toJSON();
        
        // Notificar o backend sobre o cancelamento
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const token = localStorage.getItem('token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        try {
          await axios.post(`${apiUrl}/api/auth/push/unsubscribe/`, { endpoint: subJSON.endpoint }, { headers });
        } catch (e) {
          console.warn('Erro ao notificar cancelamento ao backend (continuando desinscrição local):', e);
        }

        // Cancelar no navegador
        await subscription.unsubscribe();
        setIsSubscribed(false);
        console.log('Assinatura cancelada com sucesso no navegador.');
      }
      setLoading(false);
      return true;
    } catch (err) {
      console.error('Erro ao cancelar assinatura no navegador:', err);
      setLoading(false);
      return false;
    }
  };

  // 4. Atualizar preferências de forma dinâmica sem precisar se reinscrever
  const updatePreferences = async (chosenTime, enabled = true) => {
    try {
      setLoading(true);
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (!subscription) {
        setLoading(false);
        return false;
      }

      const subJSON = subscription.toJSON();
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const payload = {
        endpoint: subJSON.endpoint,
        preferred_time: chosenTime,
        enabled: enabled,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'America/Sao_Paulo'
      };

      await axios.patch(`${apiUrl}/api/auth/push/preferences/`, payload, { headers });
      
      setPreferredTime(chosenTime);
      setLoading(false);
      return true;
    } catch (err) {
      console.error('Erro ao atualizar preferências de Web Push no Django:', err);
      setLoading(false);
      return false;
    }
  };

  return {
    permission,
    isSubscribed,
    preferredTime,
    loading,
    subscribeUser,
    unsubscribeUser,
    updatePreferences,
    isSupported: 'Notification' in window && 'serviceWorker' in navigator,
  };
}
