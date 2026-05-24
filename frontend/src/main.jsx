import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/globals.css'
import App from './app/App.jsx'
import { initSentry } from './observability/sentry'

// 1. Recuperação de Falha de Chunks Dinâmicos (Auto-cura de Deploys Rápidos)
if (typeof window !== 'undefined') {
  window.addEventListener('vite:preloadError', (event) => {
    console.warn('[CAPIO PWA] Falha de pré-carregamento do Vite detectada. Auto-curando por recarregamento...', event.payload);
    window.location.reload(true);
  });
  
  window.addEventListener('error', (event) => {
    const errorMsg = event.message || '';
    const isChunkError = 
      errorMsg.includes('Importing a module script failed') || 
      errorMsg.includes('ChunkLoadError') ||
      errorMsg.includes('failed to fetch dynamically imported module');
      
    if (isChunkError) {
      console.warn('[CAPIO PWA] Falha global de script capturada. Auto-curando...', errorMsg);
      window.location.reload(true);
    }
  }, true); // true ativa fase de captura para pegar erros de tags de script e stylesheets
}

initSentry()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
