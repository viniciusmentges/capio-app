import React, { useState, useEffect, useRef } from 'react';
import { Maximize, Minimize } from 'lucide-react';

const PresentationViewer = ({ slug }) => {
  const [status, setStatus] = useState('loading'); // 'loading', 'success', 'not-found'
  const [controlsVisible, setControlsVisible] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef(null);
  const iframeRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    const checkExistence = async () => {
      try {
        const res = await fetch(`/presentations/${slug}/index.html`);
        if (!res.ok) {
          setStatus('not-found');
          return;
        }
        const text = await res.text();
        // Se a resposta for o index.html principal do React (fallback de SPA), vai conter src="/src/main.jsx" ou algo parecido
        if (text.includes('id="root"') && (text.includes('main.jsx') || text.includes('main.tsx') || text.includes('CAPIO'))) {
          setStatus('not-found');
        } else {
          setStatus('success');
        }
      } catch (error) {
        setStatus('not-found');
      }
    };
    checkExistence();
  }, [slug]);

  const wakeControls = () => {
    setControlsVisible(true);
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      setControlsVisible(false);
    }, 3000);
  };

  useEffect(() => {
    if (status !== 'success') return;

    // Listeners na janela principal (wrapper)
    window.addEventListener('mousemove', wakeControls);
    window.addEventListener('touchstart', wakeControls);
    window.addEventListener('keydown', wakeControls);

    wakeControls();

    return () => {
      window.removeEventListener('mousemove', wakeControls);
      window.removeEventListener('touchstart', wakeControls);
      window.removeEventListener('keydown', wakeControls);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [status]);

  const handleIframeLoad = () => {
    try {
      const iframeWin = iframeRef.current?.contentWindow;
      const iframeDoc = iframeWin?.document;
      if (iframeDoc) {
        // Injetar listeners de inatividade dentro do iframe também, pois ele consome os eventos
        iframeDoc.addEventListener('mousemove', wakeControls);
        iframeDoc.addEventListener('touchstart', wakeControls);
        iframeDoc.addEventListener('keydown', wakeControls);
      }
      
      // Auto-focus para teclado funcionar imediatamente sem precisar clicar
      if (iframeWin) {
        iframeWin.focus();
      }
    } catch (e) {
      console.warn("Could not attach listeners to iframe due to cross-origin or other error", e);
    }
  };

  const toggleFullscreen = async () => {
    if (!document.fullscreenElement) {
      try {
        if (containerRef.current?.requestFullscreen) {
          await containerRef.current.requestFullscreen();
          setIsFullscreen(true);
        } else if (containerRef.current?.webkitRequestFullscreen) {
          await containerRef.current.webkitRequestFullscreen(); // Safari
          setIsFullscreen(true);
        }
      } catch (err) {
        console.error("Erro ao tentar entrar em fullscreen:", err);
      }
    } else {
      if (document.exitFullscreen) {
        await document.exitFullscreen();
        setIsFullscreen(false);
      } else if (document.webkitExitFullscreen) {
        await document.webkitExitFullscreen(); // Safari
        setIsFullscreen(false);
      }
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement || !!document.webkitFullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
    };
  }, []);

  if (status === 'loading') {
    return <div className="min-h-[100dvh] w-full flex items-center justify-center bg-zinc-950 text-white font-sans">Carregando apresentação...</div>;
  }

  if (status === 'not-found') {
    return (
      <div className="min-h-[100dvh] w-full flex flex-col items-center justify-center bg-zinc-950 text-zinc-300 font-sans p-6 text-center">
        <h1 className="text-3xl font-semibold mb-4 text-white">Apresentação não encontrada</h1>
        <p className="max-w-md text-zinc-400 mb-8">
          A apresentação que você tentou acessar não existe ou foi removida. Verifique o link e tente novamente.
        </p>
        <button 
          onClick={() => window.location.href = '/'}
          className="px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors cursor-pointer"
        >
          Voltar ao início
        </button>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef} 
      className={`relative w-full h-[100dvh] bg-black overflow-hidden flex flex-col ${!controlsVisible && isFullscreen ? 'cursor-none' : ''}`}
    >
      <iframe
        ref={iframeRef}
        src={`/presentations/${slug}/index.html`}
        className="flex-grow w-full h-full border-none"
        onLoad={handleIframeLoad}
        sandbox="allow-scripts allow-same-origin allow-presentation allow-popups"
        title={`Presentation: ${slug}`}
      />

      {/* Controles Flutuantes */}
      <div 
        className={`absolute bottom-6 right-6 flex gap-3 transition-opacity duration-500 z-50 ${controlsVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
      >
        <button
          onClick={toggleFullscreen}
          className="p-3 bg-black/60 hover:bg-black/80 backdrop-blur-md text-white rounded-full transition-all shadow-lg border border-white/10 cursor-pointer"
          aria-label={isFullscreen ? "Sair da tela cheia" : "Tela cheia"}
          title={isFullscreen ? "Sair da tela cheia" : "Tela cheia"}
        >
          {isFullscreen ? <Minimize size={24} /> : <Maximize size={24} />}
        </button>
      </div>
    </div>
  );
};

export default PresentationViewer;
