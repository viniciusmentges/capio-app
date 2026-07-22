import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useSEO } from '../../hooks/useSEO';
import { capturePageView, captureEvent } from '../../analytics/posthogClient';

export default function ObrasPage() {
  useSEO({
    title: 'Obras da CAPIO — Edições CAPIO',
    description: 'Conheça as obras contemplativas publicadas pela CAPIO.',
    url: 'https://capio.app/obras',
  });

  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (typeof captureEvent === 'function') {
        captureEvent('obras_page_view');
    }
  }, []);

  return (
    <div className={`min-h-[100dvh] bg-background text-foreground flex flex-col items-center selection:bg-border/30 transition-opacity duration-[2000ms] ease-out ${mounted ? 'opacity-100' : 'opacity-0'}`}>
      
      <main className="w-full max-w-lg mx-auto px-6 pt-16 pb-32">
        
        {/* CABEÇALHO */}
        <div className="text-center mb-16 animate-fade-in">
          <p className="text-[10px] font-medium uppercase tracking-[0.3em] text-accent">
            CAPIO
          </p>
        </div>

        {/* HERO E DESCRIÇÃO */}
        <section className="space-y-6 animate-fade-in text-center" style={{ animationDelay: '150ms' }}>
          <h1 className="text-3xl md:text-4xl font-serif tracking-tight leading-[1.15] text-foreground/90">
            Edições CAPIO
          </h1>
          <p className="text-foreground/70 font-serif italic text-lg leading-relaxed max-w-sm mx-auto">
            Obras construídas para aproximar a Palavra das diferentes estações da vida comum.
          </p>
        </section>

        {/* CATÁLOGO DE OBRAS */}
        <section className="mt-20 space-y-12 animate-fade-in" style={{ animationDelay: '300ms' }}>
          
          {/* Card: Para quando tudo parece pesado */}
          <article className="group flex flex-col md:flex-row items-center md:items-stretch bg-surface border border-border/40 rounded-sm shadow-sm overflow-hidden hover:border-accent/30 transition-colors">
              
              {/* Mockup Minimalista no Card */}
              <div className="w-full md:w-48 h-64 bg-background border-b md:border-b-0 md:border-r border-border/40 flex items-center justify-center relative overflow-hidden flex-shrink-0">
                  <div className="absolute top-4 left-4 right-4 text-left">
                      <p className="text-[8px] uppercase tracking-widest text-foreground/40 mb-2">Capio</p>
                      <p className="font-serif text-sm leading-snug text-foreground/80">Para quando<br/>tudo parece<br/>pesado</p>
                  </div>
              </div>

              <div className="p-6 md:p-8 flex flex-col justify-center text-center md:text-left space-y-4">
                  <div className="space-y-2">
                      <span className="inline-block bg-accent/10 text-accent text-[8px] uppercase tracking-widest px-2 py-1 rounded-sm mb-2">
                          Gratuita
                      </span>
                      <h2 className="text-xl font-serif text-foreground/90 leading-tight">
                          Para quando tudo parece pesado
                      </h2>
                  </div>
                  
                  <p className="text-sm font-light text-foreground/70 leading-relaxed">
                      Sete devocionais para reencontrar esperança, silêncio e descanso na Palavra.
                  </p>
                  
                  <div className="pt-2">
                      <Link 
                          to="/obras/para-quando-tudo-parece-pesado" 
                          onClick={() => {
                              if (typeof captureEvent === 'function') {
                                  captureEvent('click_obra_card', { obra: 'Para quando tudo parece pesado' });
                              }
                          }}
                          className="inline-block text-[10px] font-sans font-medium uppercase tracking-[0.25em] text-accent transition-colors underline underline-offset-8 decoration-accent/20 hover:decoration-accent/50 py-2"
                      >
                          Conhecer a obra
                      </Link>
                  </div>
              </div>
          </article>

        </section>

        {/* Footer */}
        <footer className="pt-24 flex flex-col items-center space-y-8">
          <div className="w-1.5 h-1.5 bg-foreground/10 rounded-full" />
          <p className="text-[9px] uppercase tracking-[0.2em] text-foreground/20">
            CAPIO &copy; {new Date().getFullYear()}
          </p>
        </footer>

      </main>
    </div>
  );
}
