import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import { getGreetingContext, formatFirstName } from '../../utils/greeting';
import { getTodayReflection, getNightReflection, getLiturgicalArchive, getSpiritualJourney } from '../../lib/reflection';

export default function HomePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // 1. Determinar período do dia
  const currentHour = new Date().getHours();
  const isNight = currentHour >= 18 || currentHour < 5;

  // 2. Fetch de dados do backend
  const { data: reflectionData, isLoading: isReflectionLoading } = useQuery({
    queryKey: ['reflection', 'today'],
    queryFn: getTodayReflection,
    staleTime: 1000 * 60 * 60,
  });

  const { data: nightData } = useQuery({
    queryKey: ['reflection', 'night', 'v2'],
    queryFn: getNightReflection,
    enabled: isNight,
    staleTime: 1000 * 60 * 60,
  });

  const { data: archiveData } = useQuery({
    queryKey: ['reflection', 'liturgical-archive'],
    queryFn: getLiturgicalArchive,
    staleTime: 1000 * 60 * 60,
  });

  const { data: journeyData } = useQuery({
    queryKey: ['reflection', 'spiritual-journey'],
    queryFn: getSpiritualJourney,
    staleTime: 1000 * 60 * 60,
  });

  const greeting = getGreetingContext();
  const firstName = formatFirstName(user);
  const title = firstName ? `${greeting}, ${firstName}.` : `${greeting}.`;

  useEffect(() => {
    if (isNight) {
      document.body.classList.add('capio-night-theme');
    } else {
      document.body.classList.remove('capio-night-theme');
    }

    return () => {
      document.body.classList.remove('capio-night-theme');
    };
  }, [isNight]);

  const getReflectionPreview = () => {
    if (isReflectionLoading) return "Preparando sua reflexão...";
    if (!reflectionData || !reflectionData.reflection) return "A leitura de hoje aguarda em silêncio.";
    return reflectionData.reflection.reflection_body || reflectionData.reflection.title || "";
  };

  return (
    <div className={`space-y-16 animate-fade-in pb-24 ${isNight ? 'capio-night-theme' : ''}`}>
      
      {/* Bloco 1: Saudação Contextual e Contemplativa */}
      <section className="space-y-4 pt-4">
        <h1 className="text-3xl font-serif tracking-tight">
          {title}
        </h1>
        <p className="text-foreground/45 font-sans font-light tracking-wide text-xs">
          {isNight 
            ? "Encontre repouso e silêncio ao fechar este dia." 
            : "Que este momento seja vivido com calma e atenção plena."
          }
        </p>
      </section>

      {/* Bloco 2: Devocional (Card de Papel) */}
      <section>
        <div 
          onClick={() => navigate('/devotional/emotions')}
          className="relative overflow-hidden flex flex-col space-y-3 cursor-pointer transition-all hover:bg-[#f6f4f0] group"
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === 'Enter') navigate('/devotional/emotions') }}
          style={{
            backgroundColor: '#FCFBF8',
            border: '1px solid #E6E1D8',
            borderRadius: '24px',
            padding: '32px',
            boxShadow: 'none'
          }}
        >
          {/* Elemento orgânico sutil (Ramo botânico) */}
          <svg 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="0.5" 
            strokeLinecap="round"
            strokeLinejoin="round"
            className="absolute -right-4 -bottom-4 w-32 h-32 text-[#A68463] opacity-[0.08] pointer-events-none transform -rotate-12"
          >
            <path d="M12 22c0-8 4-12 8-16M12 18c-3-2-6-2-8-4M13 14c4-2 7-1 9 2M11 10c-3-2-6-1-8 2" />
          </svg>

          <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-[#A68463]">
            Devocional
          </p>
          <div className="space-y-1.5 z-10 relative">
            <h2 className="text-xl font-serif text-foreground/80 leading-snug">
              Como está seu coração hoje?
            </h2>
            <p className="text-foreground/50 font-sans text-[11px] font-light max-w-[85%] leading-relaxed">
              Escolha uma emoção e receba um devocional preparado para este momento.
            </p>
          </div>
          <div className="pt-2 z-10 relative">
            <span className="inline-block text-[9px] font-sans font-medium uppercase tracking-[0.25em] text-[#A68463] transition-colors underline underline-offset-8 decoration-[#A68463]/20 group-hover:decoration-[#A68463]/50">
              Silenciar e escolher
            </span>
          </div>
        </div>
      </section>

      {/* Bloco 3: Reflexão de Hoje (O Centro Absoluto) */}
      <section className="space-y-6 pt-4 border-t border-foreground/[0.015]">
        <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-foreground/35">
          Reflexão do Dia
        </p>
        {isReflectionLoading ? (
          <div className="py-8 space-y-4 animate-pulse">
            <div className="h-4 bg-foreground/5 rounded w-3/4"></div>
            <div className="h-4 bg-foreground/5 rounded w-5/6"></div>
            <div className="h-4 bg-foreground/5 rounded w-2/3"></div>
            <p className="text-xs font-serif italic text-foreground/30 pt-2">
              A leitura de hoje aguarda em silêncio...
            </p>
          </div>
        ) : (
          <div className="space-y-8">
            <h2 className="text-xl font-serif italic text-foreground/75 leading-snug">
              {reflectionData?.reflection?.title || "Algo reservado para este dia"}
            </h2>
            <p className="text-contemplative text-foreground/80 line-clamp-4 leading-relaxed">
              {getReflectionPreview()}
            </p>
            <div className="pt-2">
              <button 
                onClick={() => navigate('/reflection/today')}
                className="text-[9px] font-sans font-medium uppercase tracking-[0.25em] text-foreground/45 hover:text-foreground/85 transition-colors underline underline-offset-8 decoration-foreground/10 hover:decoration-foreground/30 py-2 cursor-pointer"
              >
                Mergulhar na leitura
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Bloco 4: Palavra da Noite (Sessão Noturna Dinâmica) */}
      {isNight && nightData && nightData.night_word && (
        <section className="space-y-8 pt-8 border-t border-foreground/[0.015] animate-fade-in max-w-lg">
          <p className="text-[9px] font-sans font-light uppercase tracking-[0.25em] text-foreground/35">
            Palavra da Noite
          </p>
          <div className="space-y-6">
            <blockquote className="font-serif italic text-lg text-foreground/80 leading-relaxed">
              “{nightData.night_word}”
            </blockquote>
            <p className="text-[9px] uppercase tracking-[0.2em] font-sans font-light text-foreground/45">
              — {nightData.scripture_reference}
            </p>
            <div className="space-y-2 pt-6 border-t border-foreground/[0.02]">
              <p className="text-[9px] font-sans font-light uppercase text-foreground/30 tracking-widest">
                Oração de encerramento
              </p>
              <p className="font-serif text-sm text-foreground/60 italic leading-relaxed">
                {nightData.night_prayer}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Bloco 5: Memória Espiritual / Observação Pastoral */}
      {journeyData && journeyData.show_journey && journeyData.journey_text && (
        <section className="space-y-4 pt-8 border-t border-foreground/[0.015] max-w-md animate-fade-in">
          <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-foreground/35">
            Observação Pastoral
          </p>
          <p className="font-serif italic text-sm text-foreground/55 leading-relaxed">
            "{journeyData.journey_text}"
          </p>
        </section>
      )}

      {/* Bloco 6: Diário Litúrgico (Arquivo Silencioso) */}
      {archiveData && archiveData.length > 1 && (
        <section className="space-y-6 pt-8 border-t border-foreground/[0.015]">
          <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-foreground/35">
            Diário Litúrgico
          </p>
          <div className="space-y-4 max-w-md">
            {archiveData.slice(1, 4).map((ref, idx) => {
              const label = idx === 0 ? "Ontem" : idx === 1 ? "Anteontem" : "Esta semana";
              return (
                <div key={ref.id} className="flex justify-between items-center py-2 border-b border-foreground/[0.02]">
                  <div className="space-y-1">
                    <span className="text-[9px] font-sans font-light uppercase tracking-wider text-foreground/30">
                      {label}
                    </span>
                    <p className="font-serif text-sm text-foreground/75 italic">
                      {ref.title}
                    </p>
                  </div>
                  <Link 
                    to={`/share/reflection/${ref.id}`} 
                    className="text-[9px] uppercase tracking-wider text-foreground/40 hover:text-foreground/75 transition-colors underline decoration-foreground/10"
                  >
                    Revisitar
                  </Link>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Bloco de Apoio - Discreto e Contextual */}
      <section className="pt-12 border-t border-foreground/[0.01]">
        <div className="space-y-3">
          <p className="text-[9px] font-sans font-light text-foreground/35 leading-relaxed max-w-xs">
            A CAPIO é mantida por quem a utiliza de forma totalmente voluntária. Considere apoiar o projeto.
          </p>
          <Link 
            to="/apoie" 
            className="inline-block text-[9px] uppercase tracking-[0.2em] text-foreground/45 hover:text-foreground/80 underline underline-offset-4 decoration-foreground/10 transition-colors"
          >
            Ajudar a causa
          </Link>
        </div>
      </section>

      {/* Bloco de Rodapé - Discreto e Contemplativo */}
      <footer className="pt-16 space-y-12">
        <div className="w-1.5 h-1.5 bg-foreground/10 rounded-full mx-auto" />
        
        <div className="flex flex-col items-center space-y-8">
          <button 
            onClick={logout}
            className="text-[9px] uppercase tracking-[0.2em] text-foreground/20 hover:text-foreground/40 transition-colors"
          >
            Sair da conta
          </button>
        </div>
      </footer>

    </div>
  );
}
