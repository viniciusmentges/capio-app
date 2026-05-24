import React, { useEffect } from 'react';
import { useRouteError } from 'react-router-dom';
import Button from './Button';
import { captureException } from '../../observability/sentry';

export default function ContemplativeErrorBoundary() {
  const error = useRouteError();

  useEffect(() => {
    const errorStr = error?.message || String(error || '');
    console.error('[CAPIO ContemplativeErrorBoundary] Rota falhou:', error);

    // Enviar erro ao Sentry/logs de observabilidade
    captureException(error, {
      tags: { area: 'react_router_error_element' },
      extra: { error_string: errorStr }
    });

    // Detectar erro de carregamento de chunk (ChunkLoadError / script load failed)
    const isChunkError = 
      errorStr.includes('Importing a module script failed') ||
      errorStr.includes('failed to fetch dynamically imported module') ||
      errorStr.includes('ChunkLoadError') ||
      errorStr.includes('Failed to fetch');

    if (isChunkError) {
      console.warn('[CAPIO RESILIENCE] Falha de importação de chunk detectada. Forçando auto-cura imediata por recarregamento...');
      try {
        localStorage.setItem('capio_chunk_failure_recovered', 'true');
      } catch (e) {}
      window.location.reload(true);
    }
  }, [error]);

  const handleRestart = () => {
    window.location.href = '/';
  };

  return (
    <div className="flex flex-col justify-center items-center min-h-[100dvh] px-6 text-center bg-background text-foreground animate-fade-in">
      <div className="space-y-6 max-w-sm mx-auto">
        <div className="w-12 h-px bg-foreground/10 mx-auto mb-6" />
        <h1 className="font-serif text-2xl text-foreground/80 tracking-tight leading-tight">
          Estamos preparando novamente este espaço.
        </h1>
        <p className="font-serif italic text-sm text-foreground/45 leading-relaxed">
          Houve uma interrupção silenciosa. Estamos reorganizando este momento.
        </p>
      </div>

      <div className="pt-10 max-w-xs mx-auto w-full">
        <Button
          onClick={handleRestart}
          className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
        >
          Recomeçar o silêncio
        </Button>
      </div>
    </div>
  );
}
