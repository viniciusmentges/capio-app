import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { CacheFirst, StaleWhileRevalidate, NetworkFirst } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';

// Limpa caches antigos de versões anteriores
cleanupOutdatedCaches();

// Precaching automático do App Shell (gerado pelo Vite)
precacheAndRoute(self.__WB_MANIFEST || []);

// 1. Cache de Fontes do Google (Cache First)
// Cacheia as folhas de estilo
registerRoute(
  ({ url }) => url.origin === 'https://fonts.googleapis.com',
  new CacheFirst({
    cacheName: 'google-fonts-stylesheets',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
    ],
  })
);

// Cacheia os arquivos de fonte (.woff2) por até 1 ano
registerRoute(
  ({ url }) => url.origin === 'https://fonts.gstatic.com',
  new CacheFirst({
    cacheName: 'google-fonts-webfonts',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxAgeSeconds: 60 * 60 * 24 * 365,
        maxEntries: 30,
      }),
    ],
  })
);

// 2. Cache de Imagens e Favicons (Stale While Revalidate)
registerRoute(
  ({ request }) => request.destination === 'image',
  new StaleWhileRevalidate({
    cacheName: 'capio-images',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 60,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 dias
      }),
    ],
  })
);

// 3. Cache de APIs Dinâmicas (Network First)
// Cacheia chamadas para reflexões, devocionais e passagens bíblicas com tolerância de até 7 dias offline
// Garante também exclusão absoluta de qualquer endpoint de autenticação
registerRoute(
  ({ url }) => 
    (url.pathname.startsWith('/api/reflection/') || 
     url.pathname.startsWith('/api/devotional/') || 
     url.pathname.startsWith('/api/bible/')) && 
    !url.pathname.includes('/api/auth/'),
  new NetworkFirst({
    cacheName: 'capio-api-content-v1',
    plugins: [
      new CacheableResponsePlugin({
        statuses: [0, 200],
      }),
      new ExpirationPlugin({
        maxEntries: 20,
        maxAgeSeconds: 7 * 24 * 60 * 60, // 7 dias
      }),
    ],
  })
);

// 4. Ativação Imediata do Service Worker
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// ==========================================
// ARQUITETURA WEB PUSH NOTIFICATIONS
// ==========================================

// Listener para receber eventos de push do servidor
self.addEventListener('push', (event) => {
  let payload = {
    title: 'CAPIO',
    body: 'Um convite silencioso para o seu momento diário de presença.',
    url: '/'
  };

  if (event.data) {
    try {
      payload = event.data.json();
    } catch (e) {
      payload.body = event.data.text();
    }
  }

  const options = {
    body: payload.body,
    icon: '/pwa-192x192.png',
    badge: '/pwa-192x192.png',
    data: {
      url: payload.url || '/'
    },
    // Estilo contemplativo e limpo
    tag: 'capio-daily-invite',
    renotify: true,
    silent: false // Silencioso no sentido de paz, mas emite o som padrão se o usuário tiver ativado
  };

  event.waitUntil(
    self.registration.showNotification(payload.title, options)
  );
});

// Listener para gerenciar cliques na notificação
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  const targetUrl = new URL(event.notification.data?.url || '/', self.location.origin).href;

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      // Se já tiver uma aba da CAPIO aberta, foca nela e navega para o link correto
      for (let i = 0; i < windowClients.length; i++) {
        const client = windowClients[i];
        if (client.url === targetUrl && 'focus' in client) {
          return client.focus();
        }
      }
      
      // Senão, se tiver qualquer aba da CAPIO aberta, foca nela e redireciona via JavaScript
      if (windowClients.length > 0) {
        const firstClient = windowClients[0];
        if ('focus' in firstClient) {
          // Podemos forçar o foco e enviar uma mensagem ou apenas mudar o link
          firstClient.navigate(targetUrl);
          return firstClient.focus();
        }
      }

      // Senão, abre uma nova janela
      if (self.clients.openWindow) {
        return self.clients.openWindow(targetUrl);
      }
    })
  );
});
