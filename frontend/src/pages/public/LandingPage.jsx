import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useSEO } from '../../hooks/useSEO';
import { capturePageView, captureEvent } from '../../analytics/posthogClient';

export default function LandingPage() {
  useSEO({
    title: 'CAPIO — Um lugar simples para encontrar Deus na Escritura',
    description: 'Reflexões cristãs para diferentes emoções e estações da vida comum.',
    url: 'https://capio.app/comece',
  });

  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (typeof captureEvent === 'function') {
        captureEvent('comece_page_view');
    }
  }, []);

  return (
    <div className={`min-h-[100dvh] bg-background text-foreground flex flex-col items-center selection:bg-border/30 transition-opacity duration-[2000ms] ease-out ${mounted ? 'opacity-100' : 'opacity-0'}`}>
      
      <main className="w-full max-w-lg mx-auto px-6 pt-16 pb-32">
        
        {/* Header Logo */}
        <div className="text-center mb-16 animate-fade-in">
          <p className="text-[10px] font-medium uppercase tracking-[0.3em] text-accent">
            CAPIO
          </p>
        </div>

        {/* Hero Section */}
        <section className="space-y-6 animate-fade-in text-center" style={{ animationDelay: '150ms' }}>
          <h1 className="text-3xl md:text-4xl font-serif tracking-tight leading-[1.15] text-foreground/90 max-w-[280px] md:max-w-xs mx-auto">
            Um lugar simples para encontrar Deus na Escritura.
          </h1>
          <div className="space-y-4">
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              Reflexões construídas para diferentes emoções e estações da vida comum.
            </p>
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              O difícil quase nunca é querer. O difícil é conseguir manter essa rotina quando o despertador toca cedo, a agenda aperta e o dia começa antes mesmo de conseguirmos respirar.
            </p>
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              Foi justamente pensando nessa realidade que a CAPIO nasceu. Não para criar mais uma obrigação, mas para facilitar um reencontro diário com a Palavra.
            </p>
          </div>
        </section>

        {/* Bloco Secundário: Obra Gratuita */}
        <section className="mt-16 bg-surface border border-border/40 p-8 rounded-sm shadow-sm text-center space-y-6 animate-fade-in" style={{ animationDelay: '300ms' }}>
            <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
                Um primeiro encontro com a CAPIO
            </p>
            <div className="space-y-2">
                <h2 className="text-xl md:text-2xl font-serif text-foreground/90 leading-tight">
                    Para quando tudo parece pesado
                </h2>
                <p className="text-sm font-light text-foreground/70 leading-relaxed max-w-xs mx-auto">
                    Sete devocionais para dias de cansaço, ansiedade e sobrecarga.
                </p>
            </div>
            <div className="pt-2">
                <Link 
                    to="/obras/para-quando-tudo-parece-pesado"
                    onClick={() => {
                        if (typeof captureEvent === 'function') {
                            captureEvent('click_comece_obra');
                        }
                    }}
                    className="inline-block bg-background border border-border/50 text-foreground py-3 px-6 rounded-sm text-[10px] font-medium uppercase tracking-widest hover:border-accent/50 transition-colors"
                >
                    Conhecer a obra
                </Link>
            </div>
        </section>

        {/* Reflexão (A Manhã) */}
        <section className="pt-16 border-t border-border mt-16">
          <div className="flex flex-col space-y-12">
            <div className="space-y-4 text-center md:text-left">
              <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
                A Manhã
              </p>
              <h2 className="text-xl md:text-2xl font-serif text-foreground/90 leading-tight">
                Antes que o seu dia comece.
              </h2>
              <div className="space-y-4">
                <p className="text-contemplative text-foreground/80 leading-relaxed">
                  Antes das notificações. Antes das conversas. Antes da correria.
                </p>
                <p className="text-contemplative text-foreground/80 leading-relaxed">
                  Reserve dois minutos para lembrar aquilo que realmente sustenta o restante do seu dia.
                </p>
                <p className="text-contemplative text-foreground/80 leading-relaxed">
                  É para isso que existe a Reflexão do Dia.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Devocional (O Tempo) */}
        <section className="space-y-5 pt-12 border-t border-border mt-12 text-center md:text-left">
          <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
            O Tempo
          </p>
          <h2 className="text-xl md:text-2xl font-serif text-foreground/90 leading-snug">
            O momento de permanecer.
          </h2>
          <div className="space-y-4">
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              Há dias em que uma breve reflexão basta.
              Em outros, o coração pede mais tempo.
            </p>
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              O Devocional foi pensado para esses momentos.
              Um espaço para permanecer na Palavra sem pressa.
              Ler. Meditar. Orar. E deixar que Deus fale com calma.
            </p>
          </div>
        </section>

        {/* Bíblia (A Palavra) */}
        <section className="pt-12 border-t border-border mt-12 text-center md:text-left">
          <div className="flex flex-col space-y-12">
            <div className="space-y-4">
              <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
                A Palavra
              </p>
              <h2 className="text-xl md:text-2xl font-serif text-foreground/90 leading-tight">
                A Palavra não precisa ficar na estante.
              </h2>
              <div className="space-y-4">
                <p className="text-contemplative text-foreground/80 leading-relaxed">
                  Na missa. No culto. Durante um estudo bíblico.
                  Ou naquele momento em que você simplesmente precisa voltar ao texto.
                </p>
                <p className="text-contemplative text-foreground/80 leading-relaxed">
                  A Bíblia continua perto.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Explicações (O Entendimento) */}
        <section className="space-y-5 pt-12 border-t border-border mt-12 text-center md:text-left">
          <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
            O Entendimento
          </p>
          <h2 className="text-xl md:text-2xl font-serif text-foreground/90 leading-snug">
            Compreenda aquilo que está lendo.
          </h2>
          <div className="space-y-4">
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              Algumas passagens são simples.
              Outras fazem a gente parar e perguntar:
              "O que Deus queria dizer aqui?"
            </p>
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              A CAPIO ajuda você a compreender essas passagens sem complicar a linguagem e sem perder o respeito pela Escritura.
            </p>
          </div>
        </section>

        {/* Noite (O Descanso) */}
        <section className="mt-16 capio-night-theme bg-surface border border-border/40 rounded-sm p-8 space-y-8 shadow-sm transition-colors text-center md:text-left">
          <div className="space-y-4">
            <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
              O Descanso
            </p>
            <h2 className="text-xl md:text-2xl font-serif text-foreground/90 leading-snug">
              Termine o dia da mesma forma que começou.
            </h2>
            <div className="space-y-4">
              <p className="text-contemplative text-foreground/80 leading-relaxed">
                Quando a noite chega, tudo desacelera.
              </p>
              <p className="text-contemplative text-foreground/80 leading-relaxed">
                A CAPIO prepara uma palavra breve para ajudar você a encerrar o dia perto de Deus.
              </p>
              <p className="text-contemplative text-foreground/80 leading-relaxed">
                Uma última mensagem.<br />
                Uma última oração.<br />
                Um último silêncio antes do descanso.
              </p>
            </div>
          </div>
        </section>

        {/* CTA Final */}
        <section className="space-y-8 pt-20 border-t border-border flex flex-col items-center text-center">
          <div className="space-y-6">
            <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
              O Próximo Passo
            </p>
            <h2 className="text-2xl md:text-3xl font-serif italic text-foreground/80 leading-snug max-w-sm mx-auto">
              Porque uma vida com Deus não é construída em um único grande momento.
            </h2>
            <p className="text-contemplative text-foreground/80 max-w-[280px] mx-auto leading-relaxed">
              É construída em pequenos encontros, todos os dias.
            </p>
          </div>
          
          <div className="pt-8 flex flex-col items-center space-y-6">
            <Link 
              to="/register" 
              onClick={() => {
                  if (typeof captureEvent === 'function') {
                      captureEvent('click_comece_signup');
                  }
              }}
              className="inline-block text-[10px] font-sans font-medium uppercase tracking-[0.25em] text-accent transition-colors underline underline-offset-8 decoration-accent/20 hover:decoration-accent/50 py-3 px-6"
            >
              Criar minha conta gratuitamente
            </Link>
            <Link 
              to="/login" 
              onClick={() => {
                  if (typeof captureEvent === 'function') {
                      captureEvent('click_comece_login');
                  }
              }}
              className="text-[9px] font-sans font-light uppercase tracking-[0.25em] text-foreground/35 hover:text-foreground/50 transition-colors"
            >
              Ou retorne à sua leitura
            </Link>
          </div>
        </section>

        {/* Footer */}
        <footer className="pt-16 flex flex-col items-center space-y-8">
          <div className="w-1.5 h-1.5 bg-foreground/10 rounded-full" />
          <p className="text-[9px] uppercase tracking-[0.2em] text-foreground/20">
            CAPIO &copy; {new Date().getFullYear()}
          </p>
        </footer>

      </main>
    </div>
  );
}
