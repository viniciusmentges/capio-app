import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useSEO } from '../../hooks/useSEO';
import LandingScreenshot from '../../components/landing/LandingScreenshot';
import { api } from '../../lib/api';

const fetchScreenshots = async () => {
  try {
    const { data } = await api.get('/public/landing-screenshots/');
    return data;
  } catch (err) {
    console.error('Failed to fetch screenshots', err);
    return [];
  }
};

export default function LandingPage() {
  useSEO({
    title: 'CAPIO — Um lugar simples para encontrar Deus na Escritura.',
    description: 'Leia a Palavra, ore com simplicidade e encontre um momento diário de descanso com Deus.',
    url: 'https://capio.app/comece',
  });

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const { data: screenshots = [] } = useQuery({
    queryKey: ['landingScreenshots'],
    queryFn: fetchScreenshots,
    staleTime: 1000 * 60 * 60, // 1 hour
  });

  const getScreenshot = (key) => screenshots.find(s => s.key === key);

  const homeScreenshot = getScreenshot('home');
  const reflexaoScreenshot = getScreenshot('reflexao');
  const bibliaScreenshot = getScreenshot('biblia');
  const noiteScreenshot = getScreenshot('noite');

  return (
    <div 
      className={`min-h-[100dvh] bg-background text-foreground safe-x safe-top safe-bottom flex flex-col items-center selection:bg-border/30 transition-opacity duration-[2000ms] ease-out ${mounted ? 'opacity-100' : 'opacity-0'}`}
    >
      
      {/* 1. Hero */}
      <section className="w-full max-w-[50ch] text-center mt-40 md:mt-56 mb-40 px-6">
        <h1 className="font-serif text-3xl md:text-4xl text-foreground/90 tracking-tight leading-[1.2] mb-12">
          Um lugar simples para encontrar Deus na Escritura.
        </h1>
        <p className="font-serif text-lg text-foreground/60 leading-relaxed">
          Todos os dias, um pequeno momento preparado para ler, compreender e permanecer na Palavra.
        </p>
      </section>

      {/* 2. Pausa Emocional */}
      <section className="w-full max-w-[45ch] text-center mb-32 px-6">
        <p className="font-serif text-xl md:text-2xl text-foreground/80 leading-[1.8] italic">
          Sabemos como a rotina pesa. 
          <br /><br />
          O despertador toca cedo, o tempo escapa e o silêncio parece impossível.
          <br /><br />
          Mas a graça nos encontra no chão da nossa imperfeição comum.
        </p>
      </section>

      <LandingScreenshot 
        src={homeScreenshot?.image_url} 
        alt={homeScreenshot?.alt_text || "Abertura do dia na CAPIO"} 
        placeholderText="Imagem da Home da CAPIO"
      />

      {/* 3. A Rotina - Manhã */}
      <section className="w-full max-w-[50ch] mt-32 mb-20 px-6 text-center">
        <p className="font-serif text-lg md:text-xl text-foreground/80 leading-[1.8]">
          A folha vira. O barulho cessa. <br /><br />
          Uma reflexão honesta e simples aguarda para iniciar o dia na companhia de Deus. 
          Lemos a Escritura juntos, para lembrar da fidelidade do Senhor antes mesmo de sair de casa.
        </p>
      </section>

      <LandingScreenshot 
        src={reflexaoScreenshot?.image_url} 
        alt={reflexaoScreenshot?.alt_text || "Leitura devocional diária"} 
        placeholderText="Imagem da Reflexão do Dia"
      />

      {/* 4. A Rotina - Bíblia */}
      <section className="w-full max-w-[50ch] mt-32 mb-20 px-6 text-center">
        <p className="font-serif text-lg md:text-xl text-foreground/80 leading-[1.8]">
          A Escritura permanece próxima. <br /><br />
          Um ambiente sem distrações para que você possa voltar aos Salmos e aos Evangelhos a qualquer momento, lendo a Palavra viva em seu próprio ritmo.
        </p>
      </section>

      <LandingScreenshot 
        src={bibliaScreenshot?.image_url} 
        alt={bibliaScreenshot?.alt_text || "A Escritura na CAPIO"} 
        placeholderText="Imagem da Bíblia"
      />

      {/* 5. A Rotina - Noite */}
      <section className="w-full max-w-[50ch] mt-32 mb-20 px-6 text-center">
        <p className="font-serif text-lg md:text-xl text-foreground/80 leading-[1.8]">
          O repouso da alma. <br /><br />
          Quando a noite cai, a tela acompanha o cansaço dos olhos. O mesmo tema da manhã retorna brevemente, conduzindo uma oração de entrega antes do sono.
        </p>
      </section>

      <LandingScreenshot 
        src={noiteScreenshot?.image_url} 
        alt={noiteScreenshot?.alt_text || "A Palavra da noite"} 
        placeholderText="Imagem da Palavra da Noite"
      />

      {/* 6. A Caminhada Silenciosa (Prova Social Humana) */}
      <section className="w-full max-w-[45ch] text-center mt-48 mb-48 px-6">
        <p className="font-serif text-xl md:text-2xl text-foreground/70 leading-[1.8]">
          Um lugar comum. <br /><br />
          A CAPIO já faz parte da rotina de pessoas que, no meio de dias imperfeitos, decidiram reservar o silêncio necessário para ouvir a voz de Deus novamente.
        </p>
      </section>

      {/* 7. Convite Final */}
      <section className="w-full max-w-md text-center mb-56 px-6 flex flex-col items-center">
        <p className="font-serif italic text-xl text-foreground/70 mb-16 leading-relaxed">
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
      
      <footer className="w-full text-center pb-16 opacity-30 font-sans text-xs tracking-widest uppercase">
        CAPIO &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
}
