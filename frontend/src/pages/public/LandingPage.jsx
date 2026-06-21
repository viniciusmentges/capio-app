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
    <div 
      className={`min-h-[100dvh] flex flex-col items-center selection:bg-border/30 transition-opacity duration-[2000ms] ease-out ${mounted ? 'opacity-100' : 'opacity-0'}`}
    >
      
      {/* 1. Hero & Pausa Emocional - bg-background */}
      <div className="w-full bg-background text-foreground safe-x safe-top flex flex-col items-center pt-24 md:pt-32 pb-16">
        <section className="w-full max-w-[50ch] text-center mb-24 px-6">
          <h1 className="font-serif text-4xl md:text-5xl text-foreground/90 tracking-tight leading-[1.15] mb-10">
            Um lugar simples para encontrar Deus na Escritura.
          </h1>
          <p className="font-serif text-lg md:text-xl text-foreground/70 leading-relaxed">
            Todos os dias, um pequeno momento preparado para ler, compreender e permanecer na Palavra.
          </p>
        </section>

        <section className="w-full max-w-[45ch] text-center mb-16 px-6">
          <p className="font-serif text-lg md:text-xl text-foreground/80 leading-[1.9]">
            Sabemos como a rotina pesa. 
            <br /><br />
            O despertador toca cedo, o tempo escapa e o silêncio parece quase impossível.
            <br /><br />
            Mas a graça nos encontra no chão da nossa imperfeição comum.
          </p>
        </section>
      </div>

      {/* 2. Primeira Imagem (Home) & Início Rotina - bg-surface */}
      <div className="w-full bg-surface text-foreground safe-x flex flex-col items-center py-20">
        <LandingScreenshot 
          src="/images/landing/home.webp" 
          alt="Abertura do dia na CAPIO" 
          placeholderText="Imagem da Home da CAPIO"
          className="my-0 mb-20"
        />

        <section className="w-full max-w-[50ch] px-6 text-center mb-10">
          <p className="font-serif text-lg md:text-xl text-foreground/80 leading-[1.9]">
            A folha vira. O barulho cessa. <br /><br />
            Uma reflexão honesta e simples aguarda para iniciar o dia na companhia de Deus. 
            Lemos a Escritura juntos, para lembrar da fidelidade do Senhor antes mesmo de sair de casa.
          </p>
        </section>
      </div>

      {/* 3. Imagem Reflexão & A Rotina Bíblia - bg-background */}
      <div className="w-full bg-background text-foreground safe-x flex flex-col items-center py-20">
        <LandingScreenshot 
          src="/images/landing/reflexao.webp" 
          alt="Leitura devocional diária" 
          placeholderText="Imagem da Reflexão do Dia"
          className="my-0 mb-20"
        />

        <section className="w-full max-w-[50ch] px-6 text-center mb-10">
          <p className="font-serif text-lg md:text-xl text-foreground/80 leading-[1.9]">
            A Escritura permanece próxima. <br /><br />
            Um ambiente sem distrações para que você possa voltar aos Salmos e aos Evangelhos a qualquer momento, lendo a Palavra viva em seu próprio ritmo.
          </p>
        </section>
      </div>

      {/* 4. Imagem Bíblia & A Rotina Noite - bg-surface */}
      <div className="w-full bg-surface text-foreground safe-x flex flex-col items-center py-20">
        <LandingScreenshot 
          src="/images/landing/biblia.webp" 
          alt="A Escritura na CAPIO" 
          placeholderText="Imagem da Bíblia"
          className="my-0 mb-20"
        />

        <section className="w-full max-w-[50ch] px-6 text-center mb-10">
          <p className="font-serif text-lg md:text-xl text-foreground/80 leading-[1.9]">
            O repouso da alma. <br /><br />
            Quando a noite cai, a tela acompanha o cansaço dos olhos. O mesmo tema da manhã retorna brevemente, conduzindo uma oração de entrega antes do sono.
          </p>
        </section>
      </div>

      {/* 5. Tema Noturno & CTA Final */}
      <div className="w-full capio-night-theme safe-x safe-bottom flex flex-col items-center py-24">
        <LandingScreenshot 
          src="/images/landing/noite.webp" 
          alt="A Palavra da noite" 
          placeholderText="Imagem da Palavra da Noite"
          className="my-0 mb-24"
        />

        <section className="w-full max-w-[45ch] text-center mb-24 px-6">
          <p className="font-serif text-lg md:text-xl text-foreground/80 leading-[1.9]">
            Um lugar comum. <br /><br />
            A CAPIO já faz parte da rotina de pessoas que, no meio de dias imperfeitos, decidiram reservar o silêncio necessário para ouvir a voz de Deus novamente.
          </p>
        </section>

        <section className="w-full max-w-md text-center mb-16 px-6 flex flex-col items-center">
          <p className="font-serif text-xl text-foreground/80 mb-12 leading-relaxed">
            A folha já está em branco. <br/>A leitura de hoje aguarda por você.
          </p>
          <Link 
            to="/register" 
            className="inline-block px-12 py-5 border border-foreground/15 text-foreground/80 font-sans text-sm tracking-widest uppercase hover:text-brand hover:border-brand/40 transition-all duration-500 rounded-sm mb-12"
          >
            Começar minha leitura
          </Link>
          <Link 
            to="/login" 
            className="font-sans text-xs tracking-wider text-foreground/40 hover:text-brand transition-colors duration-500"
          >
            Ou retorne à sua leitura
          </Link>
        </section>
        
        <footer className="w-full text-center opacity-30 font-sans text-xs tracking-widest uppercase">
          CAPIO &copy; {new Date().getFullYear()}
        </footer>
      </div>
    </div>
  );
}
