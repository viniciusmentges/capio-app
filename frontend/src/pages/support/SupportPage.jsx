import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ProgressiveReveal from '../../components/devotional/ProgressiveReveal';
import Button from '../../components/ui/Button';
import ScrollToTop from '../../components/layout/ScrollToTop';

export default function SupportPage() {
  const pixKey = import.meta.env.VITE_PIX_KEY;
  const receiverName = import.meta.env.VITE_PIX_RECEIVER_NAME;
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!pixKey) return;
    navigator.clipboard.writeText(pixKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 3000);
  };

  return (
    <div className="min-h-screen pb-32">
      <ScrollToTop />

      <div className="max-w-2xl mx-auto pt-24 px-6">
        
        {/* Header Discreto */}
        <header className="mb-24 text-center">
          <ProgressiveReveal delay={300}>
            <p className="text-[10px] font-serif italic text-foreground/20 uppercase tracking-[0.3em] mb-4">
              Gratidão
            </p>
            <h1 className="font-serif text-3xl text-foreground/40 italic leading-tight">
              Apoie a CAPIO
            </h1>
          </ProgressiveReveal>
        </header>

        <div className="space-y-20">
          {/* Texto Principal */}
          <section className="space-y-10">
            <ProgressiveReveal delay={800}>
              <p className="text-contemplative text-foreground/70 text-center leading-relaxed">
                A CAPIO nasceu para ser um espaço de leitura, oração e silêncio. 
                Se este projeto tem feito bem a você, sua contribuição ajuda a manter este ambiente vivo, estável e em evolução.
              </p>
            </ProgressiveReveal>

            <ProgressiveReveal delay={1500}>
              <p className="text-sm font-sans font-light text-foreground/40 text-center leading-relaxed italic max-w-md mx-auto">
                A doação é livre e não libera nenhum recurso extra. Ela apenas ajuda este projeto a continuar servindo mais pessoas.
              </p>
            </ProgressiveReveal>
          </section>

          {/* Área de Doação */}
          <section className="pt-12 border-t border-foreground/[0.03]">
            {!pixKey ? (
              <ProgressiveReveal delay={2000}>
                <div className="text-center py-8">
                  <p className="text-xs font-serif italic text-foreground/20 tracking-widest">
                    Em breve disponibilizaremos este canal de apoio.
                  </p>
                </div>
              </ProgressiveReveal>
            ) : (
              <div className="space-y-12">
                <ProgressiveReveal delay={2000}>
                  <div className="bg-foreground/[0.015] p-10 rounded-sm text-center space-y-6">
                    <p className="text-[9px] font-serif italic text-foreground/15 uppercase tracking-[0.2em]">
                      Doação via Pix
                    </p>
                    
                    <div className="space-y-2">
                      <p className="text-sm font-sans font-medium text-foreground/60 break-all select-all">
                        {pixKey}
                      </p>
                      {receiverName && (
                        <p className="text-[10px] font-sans text-foreground/30 uppercase tracking-widest">
                          {receiverName}
                        </p>
                      )}
                    </div>

                    <div className="pt-4">
                      <Button 
                        onClick={handleCopy}
                        variant="outline"
                        className="text-[10px] uppercase tracking-[0.2em] px-8"
                      >
                        {copied ? 'Chave Pix copiada' : 'Copiar chave Pix'}
                      </Button>
                      
                      <div className={`mt-4 h-4 transition-opacity duration-500 ${copied ? 'opacity-100' : 'opacity-0'}`}>
                        <p className="text-[10px] font-serif italic text-foreground/30">
                          Chave copiada com sucesso.
                        </p>
                      </div>
                    </div>
                  </div>
                </ProgressiveReveal>

                <ProgressiveReveal delay={2800}>
                  <div className="text-center">
                    <p className="text-[10px] font-serif italic text-foreground/15 leading-relaxed">
                      "Dai e dar-se-vos-á..."
                    </p>
                  </div>
                </ProgressiveReveal>
              </div>
            )}
          </section>

          {/* Navegação de Volta */}
          <footer className="pt-16 text-center">
            <ProgressiveReveal delay={3500}>
              <Link to="/" className="inline-block text-[10px] font-serif italic text-foreground/30 hover:text-foreground/50 transition-colors uppercase tracking-[0.2em]">
                Voltar para a quietude
              </Link>
            </ProgressiveReveal>
          </footer>
        </div>
      </div>
    </div>
  );
}
