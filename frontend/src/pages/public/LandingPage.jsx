import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useSEO } from '../../hooks/useSEO';
import LandingScreenshot from '../../components/landing/LandingScreenshot';

export default function LandingPage() {
  useSEO({
    title: 'CAPIO — Um lugar simples para encontrar Deus na Escritura.',
    description: 'Leia a Palavra, ore com simplicidade e encontre um momento diário de descanso com Deus.',
    url: 'https://capio.app/comece',
  });

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className={`min-h-[100dvh] bg-background text-foreground flex flex-col items-center selection:bg-border/30 transition-opacity duration-[2000ms] ease-out ${mounted ? 'opacity-100' : 'opacity-0'}`}>
      
      {/* Container principal contido, similar à largura da Home para manter foco editorial */}
      <main className="w-full max-w-lg mx-auto px-6 space-y-16 pt-16 pb-24">
        
        {/* 1. Hero */}
        <section className="space-y-6 pt-4 animate-fade-in">
          <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
            A Gramática do Silêncio
          </p>
          <h1 className="text-3xl md:text-4xl font-serif tracking-tight leading-[1.15] text-foreground/90">
            Um lugar simples para encontrar Deus na Escritura.
          </h1>
          <p className="text-foreground/55 font-sans font-light tracking-wide text-xs leading-relaxed max-w-sm">
            Todos os dias, um pequeno momento preparado para ler, compreender e permanecer na Palavra.
          </p>
        </section>

        {/* 2. Pausa Emocional */}
        <section className="space-y-5 pt-8 border-t border-border animate-fade-in" style={{ animationDelay: '150ms' }}>
          <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
            O Peso da Rotina
          </p>
          <blockquote className="font-serif italic text-lg text-foreground/75 leading-relaxed">
            "Sabemos como a rotina pesa. O despertador toca cedo, o tempo escapa e o silêncio parece quase impossível."
          </blockquote>
          <p className="text-contemplative text-foreground/80 leading-relaxed">
            Mas a graça nos encontra no chão da nossa imperfeição comum.
          </p>
        </section>

        {/* 3. A Manhã (Reflexão) */}
        <section className="space-y-6 pt-10 border-t border-border">
          <div className="space-y-3">
            <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
              O Início do Dia
            </p>
            <h2 className="text-xl font-serif text-foreground/80 leading-snug">
              A folha vira. O barulho cessa.
            </h2>
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              Uma reflexão honesta e simples aguarda para iniciar o dia na companhia de Deus. Lemos a Escritura juntos, para lembrar da fidelidade do Senhor antes mesmo de sair de casa.
            </p>
          </div>
          <div className="pt-2">
            <LandingScreenshot 
              src="/images/landing/home.webp" 
              alt="Abertura do dia na CAPIO" 
              placeholderText="Reflexão da Manhã"
            />
          </div>
        </section>

        {/* 4. A Escritura */}
        <section className="space-y-6 pt-10 border-t border-border">
          <div className="space-y-3">
            <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
              A Leitura
            </p>
            <h2 className="text-xl font-serif text-foreground/80 leading-snug">
              A Escritura permanece próxima.
            </h2>
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              Um ambiente sem distrações para que você possa voltar aos Salmos e aos Evangelhos a qualquer momento, lendo a Palavra viva em seu próprio ritmo.
            </p>
          </div>
          <div className="pt-2">
            <LandingScreenshot 
              src="/images/landing/biblia.webp" 
              alt="A Escritura na CAPIO" 
              placeholderText="Texto Bíblico"
            />
          </div>
        </section>

        {/* 5. A Noite (Isolado no Tema Noturno) */}
        <section className="mt-12 capio-night-theme bg-surface border border-border/40 rounded-sm p-6 md:p-8 space-y-8 shadow-sm transition-colors">
          <div className="space-y-3">
            <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
              O Fim do Dia
            </p>
            <h2 className="text-xl font-serif text-foreground/80 leading-snug">
              O repouso da alma.
            </h2>
            <p className="text-contemplative text-foreground/80 leading-relaxed">
              Quando a noite cai, a tela acompanha o cansaço dos olhos. O mesmo tema da manhã retorna brevemente, conduzindo uma oração de entrega antes do sono.
            </p>
          </div>
          <div className="pt-2">
            <LandingScreenshot 
              src="/images/landing/noite.webp" 
              alt="A Palavra da noite" 
              placeholderText="Palavra da Noite"
              isNight={true}
            />
          </div>
        </section>

        {/* 6. CTA Final (Integrado à narrativa) */}
        <section className="space-y-8 pt-16 border-t border-border flex flex-col items-center text-center">
          <div className="space-y-4">
            <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-accent">
              O Próximo Passo
            </p>
            <h2 className="text-2xl font-serif italic text-foreground/80 leading-snug">
              A folha já está em branco.
            </h2>
            <p className="text-foreground/55 font-sans font-light text-xs tracking-wide max-w-[250px] mx-auto leading-relaxed">
              A leitura de hoje aguarda por você.
            </p>
          </div>
          
          <div className="pt-4 flex flex-col items-center space-y-6">
            <Link 
              to="/register" 
              className="inline-block text-[10px] font-sans font-medium uppercase tracking-[0.25em] text-accent transition-colors underline underline-offset-8 decoration-accent/20 hover:decoration-accent/50 py-3 px-6"
            >
              Começar minha leitura
            </Link>
            <Link 
              to="/login" 
              className="text-[9px] font-sans font-light uppercase tracking-[0.25em] text-foreground/35 hover:text-foreground/50 transition-colors"
            >
              Ou retorne à sua leitura
            </Link>
          </div>
        </section>

        {/* 7. Footer Contemplativo */}
        <footer className="pt-12 pb-8 flex flex-col items-center space-y-8">
          <div className="w-1.5 h-1.5 bg-foreground/10 rounded-full" />
          <p className="text-[9px] uppercase tracking-[0.2em] text-foreground/20">
            CAPIO &copy; {new Date().getFullYear()}
          </p>
        </footer>

      </main>
    </div>
  );
}
