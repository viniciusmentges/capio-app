import React from 'react';
import Button from './Button';
import { captureException } from '../../observability/sentry';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[CAPIO ErrorBoundary] Falha capturada de renderizacao:', error, errorInfo);
    captureException(error, {
      tags: { area: 'react_error_boundary' },
      extra: errorInfo,
    });
  }

  handleRestart = () => {
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
              Algo ficou em silencio por um instante.
            </h1>
            <p className="font-serif italic text-sm text-foreground/45 leading-relaxed">
              Voce pode tentar novamente em alguns segundos.
            </p>
          </div>

          <div className="pt-10 max-w-xs mx-auto w-full">
            <Button
              onClick={this.handleRestart}
              className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
            >
              Recomecar o silencio
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
