import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useSEO } from '../../hooks/useSEO';
import { api } from '../../lib/api';
import { capturePageView, captureEvent } from '../../analytics/posthogClient';

export default function LandingPage() {
  useSEO({
    title: 'CAPIO — Para quando tudo parece pesado.',
    description: 'Sete encontros para os dias em que tudo parece pesado. Uma leitura gratuita para acompanhar você em dias de cansaço, ansiedade e sobrecarga.',
    url: 'https://capio.app/comece',
  });

  const [mounted, setMounted] = useState(false);
  
  // Form State
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    setMounted(true);
    // Dispara o evento de view específico desta nova landing page
    if (typeof captureEvent === 'function') {
        captureEvent('landing_comece_view');
    }
  }, []);

  const handleFocus = () => {
    if (typeof captureEvent === 'function') {
        captureEvent('lead_form_started');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !consent) {
        setError("Por favor, preencha seu e-mail e concorde em receber nossas comunicações.");
        return;
    }

    setLoading(true);
    setError('');

    try {
      const urlParams = new URLSearchParams(window.location.search);
      const payload = {
        name: name,
        email: email,
        consent_communications: consent,
        source: 'Tudo Parece Pesado',
        utm_source: urlParams.get('utm_source') || '',
        utm_medium: urlParams.get('utm_medium') || '',
        utm_campaign: urlParams.get('utm_campaign') || '',
        utm_content: urlParams.get('utm_content') || '',
        utm_term: urlParams.get('utm_term') || '',
      };

      const response = await api.post('/landing/leads/', payload);
      
      setSuccess(true);
      setSuccessMessage(response.data.message || "A obra já está a caminho do seu e-mail.");
      if (typeof captureEvent === 'function') {
          captureEvent('lead_capture_success', { is_new: response.data.is_new });
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.email?.[0] || err.response?.data?.consent_communications?.[0] || "Ocorreu um erro ao processar seu pedido. Tente novamente.");
      if (typeof captureEvent === 'function') {
          captureEvent('lead_capture_error', { error: err.message });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleShare = async () => {
    if (typeof captureEvent === 'function') {
        captureEvent('click_share_encontro');
    }
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'CAPIO — Para quando tudo parece pesado',
          text: 'Um lugar simples para encontrar descanso.',
          url: 'https://capio.app/comece',
        });
      } catch (err) {
        console.error('Share failed:', err);
      }
    } else {
      navigator.clipboard.writeText('https://capio.app/comece');
      alert('Link copiado!');
    }
  };

  return (
    <div className={`min-h-[100dvh] bg-background text-foreground flex flex-col items-center selection:bg-border/30 transition-opacity duration-[2000ms] ease-out ${mounted ? 'opacity-100' : 'opacity-0'}`}>
      
      <main className="w-full max-w-lg mx-auto px-6 pt-16 pb-32">
        
        {/* CABEÇALHO */}
        <div className="text-center mb-16 animate-fade-in">
          <p className="text-[10px] font-medium uppercase tracking-[0.3em] text-accent">
            CAPIO
          </p>
        </div>

        {/* HERO E OBRA */}
        <section className="space-y-8 animate-fade-in text-center" style={{ animationDelay: '150ms' }}>
          
          <div className="space-y-4">
            <h1 className="text-3xl md:text-4xl font-serif tracking-tight leading-[1.15] text-foreground/90">
              Para quando tudo parece pesado.
            </h1>
            <p className="text-foreground/70 font-serif italic text-lg leading-relaxed max-w-md mx-auto">
              Sete encontros para os dias em que tudo parece pesado.
            </p>
          </div>

          <p className="text-foreground/60 font-sans font-light tracking-wide text-sm leading-relaxed max-w-sm mx-auto">
            Uma leitura gratuita construída a partir da Escritura para acompanhar momentos de cansaço, ansiedade e sobrecarga.
          </p>

          <div className="py-6 flex justify-center">
            {/* Mockup Minimalista da Obra */}
            <div className="w-48 h-64 bg-surface border border-border/40 shadow-sm flex items-center justify-center rounded-sm relative overflow-hidden">
                <div className="absolute top-4 left-4 right-4 text-left">
                    <p className="text-[8px] uppercase tracking-widest text-foreground/40 mb-2">Capio</p>
                    <p className="font-serif text-sm leading-snug text-foreground/80">Para quando<br/>tudo parece<br/>pesado</p>
                </div>
                <div className="absolute bottom-4 left-4">
                    <p className="text-[8px] italic text-foreground/40">O seu primeiro encontro com a CAPIO.</p>
                </div>
            </div>
          </div>

        </section>

        {/* O QUE O LEITOR RECEBERÁ */}
        <section className="mt-16 space-y-6 animate-fade-in" style={{ animationDelay: '300ms' }}>
          <p className="text-contemplative text-foreground/80 leading-relaxed text-center">
            Sete encontros construídos a partir da Escritura, com reflexões, orações e palavras para guardar ao longo da semana.
          </p>
          <ul className="space-y-3 text-sm font-light text-foreground/70 mx-auto max-w-xs text-center list-none">
            <li>• Sete leituras contemplativas</li>
            <li>• Reflexões fundamentadas na Escritura</li>
            <li>• Acesso gratuito por e-mail</li>
          </ul>
        </section>

        {/* FORMULÁRIO OU SUCESSO */}
        <section className="mt-20 max-w-sm mx-auto animate-fade-in" style={{ animationDelay: '450ms' }}>
          
          {!success ? (
            <div className="space-y-8 bg-surface p-8 border border-border/40 rounded-sm shadow-sm">
                <div className="text-center space-y-2">
                    <h2 className="font-serif text-xl text-foreground/90">Receba seu primeiro encontro</h2>
                    <p className="text-xs text-foreground/60">Informe seu e-mail e enviaremos a obra para você.</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    {error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-500 text-xs rounded-sm text-center">
                            {error}
                        </div>
                    )}
                    <div className="space-y-4">
                        <input
                            type="text"
                            placeholder="Seu nome (opcional)"
                            className="w-full bg-background border border-border/50 rounded-sm px-4 py-3 text-sm font-light placeholder:text-foreground/30 focus:outline-none focus:border-accent/50 transition-colors"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            onFocus={handleFocus}
                        />
                        <input
                            type="email"
                            required
                            placeholder="Seu melhor e-mail"
                            className="w-full bg-background border border-border/50 rounded-sm px-4 py-3 text-sm font-light placeholder:text-foreground/30 focus:outline-none focus:border-accent/50 transition-colors"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            onFocus={handleFocus}
                        />
                        <label className="flex items-start space-x-3 cursor-pointer group pt-2">
                            <div className="mt-0.5 flex-shrink-0">
                                <input
                                    type="checkbox"
                                    required
                                    className="w-4 h-4 rounded-sm border-border/50 text-accent focus:ring-accent/50 focus:ring-offset-background bg-background"
                                    checked={consent}
                                    onChange={(e) => setConsent(e.target.checked)}
                                />
                            </div>
                            <span className="text-[11px] text-foreground/60 leading-relaxed font-light group-hover:text-foreground/80 transition-colors text-left">
                                Concordo em receber esta obra e as próximas Cartas da CAPIO por e-mail. Posso cancelar quando desejar.
                            </span>
                        </label>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-accent text-accent-foreground py-3.5 px-4 rounded-sm text-xs font-medium uppercase tracking-widest hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
                    >
                        {loading ? 'Enviando...' : 'Receber meu primeiro encontro'}
                    </button>
                </form>
            </div>
          ) : (
            <div className="space-y-8 bg-surface p-8 border border-border/40 rounded-sm shadow-sm text-center">
                <div className="w-12 h-12 mx-auto rounded-full bg-accent/10 flex items-center justify-center">
                    <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                    </svg>
                </div>
                <div className="space-y-4">
                    <h2 className="font-serif text-xl text-foreground/90">
                        {successMessage}
                    </h2>
                    <p className="text-sm text-foreground/60 font-light">
                        Enquanto ela chega, você pode conhecer a biblioteca gratuita da CAPIO.
                    </p>
                </div>
                <div className="pt-2">
                    <Link 
                        to="/register" 
                        onClick={() => {
                            if (typeof captureEvent === 'function') {
                                captureEvent('click_conhecer_app');
                            }
                        }}
                        className="inline-block w-full bg-accent text-accent-foreground py-3.5 px-4 rounded-sm text-xs font-medium uppercase tracking-widest hover:bg-accent/90 transition-colors"
                    >
                        Conhecer a CAPIO
                    </Link>
                </div>
            </div>
          )}

        </section>

        {/* APRESENTAÇÃO DO PWA */}
        <section className="mt-24 space-y-8 pt-12 border-t border-border flex flex-col items-center text-center">
          <div className="space-y-6">
            <h2 className="text-xl md:text-2xl font-serif text-foreground/80 leading-snug">
              A leitura pode continuar.
            </h2>
            <p className="text-contemplative text-foreground/70 max-w-sm mx-auto leading-relaxed">
              A CAPIO aproxima a Palavra das diferentes estações da vida comum. No aplicativo, mais de duzentas reflexões já estão abertas gratuitamente.
            </p>
          </div>
          
          <div className="pt-4">
            <Link 
              to="/register" 
              onClick={() => {
                  if (typeof captureEvent === 'function') {
                      captureEvent('click_conhecer_app');
                  }
              }}
              className="inline-block text-[10px] font-sans font-medium uppercase tracking-[0.25em] text-accent transition-colors underline underline-offset-8 decoration-accent/20 hover:decoration-accent/50 py-3 px-6"
            >
              Conhecer a CAPIO
            </Link>
          </div>
        </section>

        {/* FOOTER & COMPARTILHAMENTO */}
        <footer className="pt-24 flex flex-col items-center space-y-12">
          
          <div className="text-center space-y-4">
            <p className="text-xs text-foreground/50 font-serif italic">
                Conhece alguém atravessando dias difíceis?
            </p>
            <button 
                onClick={handleShare}
                className="text-[10px] uppercase tracking-widest text-foreground/40 hover:text-foreground/70 transition-colors flex items-center justify-center space-x-2 mx-auto"
            >
                <span>Compartilhe este encontro gratuitamente</span>
                <svg className="w-3 h-3 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
            </button>
          </div>

          <div className="w-1.5 h-1.5 bg-foreground/10 rounded-full" />
          
          <p className="text-[9px] uppercase tracking-[0.2em] text-foreground/20">
            CAPIO &copy; {new Date().getFullYear()}
          </p>
        </footer>

      </main>
    </div>
  );
}
