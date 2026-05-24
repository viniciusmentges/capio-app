import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { CacheFirst, StaleWhileRevalidate } from 'workbox-strategies';
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

// NOTA DE ARQUITETURA OFFLINE:
// As APIs dinâmicas (/api/reflection/, /api/devotional/ e /api/bible/) batem diretamente na rede (NetworkOnly)
// para evitar o efeito "ghost cache" (onde o Service Worker retorna um HTTP 200 cacheado ocultando a falha de rede do React/TanStack).
// Em caso de falha de conexão, a chamada falha nativamente, propagando o erro para o frontend, que
// aciona de forma consistente e silenciosa o IndexedDB/localForage como ÚNICA FONTE DE VERDADE offline.

// 3. Ativação Imediata do Service Worker (Prevenção de Ghost Cache)
self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
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
