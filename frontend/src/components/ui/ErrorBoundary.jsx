import React from 'react';
import Button from './Button';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Atualiza o estado para que o próximo render exiba a UI de fallback
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Registra a falha no console em desenvolvimento
    console.error('[CAPIO ErrorBoundary] Falha capturada de renderização:', error, errorInfo);
    
    // Suporte para Sentry na janela se estiver integrado futuramente
    if (window.Sentry) {
      window.Sentry.captureException(error, { extra: errorInfo });
    }
  }

  handleRestart = () => {
    // Limpa estados e recarrega a página de forma limpa
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col justify-center items-center min-h-[100dvh] px-6 text-center bg-background text-foreground animate-fade-in">
          <div className="space-y-6 max-w-sm mx-auto">
            <div className="w-12 h-px bg-foreground/10 mx-auto mb-6" />
            <h1 className="font-serif text-2xl text-foreground/80 tracking-tight leading-tight">
              Algo ficou em silêncio por um instante.
            </h1>
            <p className="font-serif italic text-sm text-foreground/45 leading-relaxed">
              Você pode tentar novamente em alguns segundos.
            </p>
          </div>
          
          <div className="pt-10 max-w-xs mx-auto w-full">
            <Button
              onClick={this.handleRestart}
              className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
            >
              Recomeçar o silêncio
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
