import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import Button from '../../components/ui/Button';
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
    queryKey: ['reflection', 'night'],
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

      {/* Bloco 2: Reflexão de Hoje (O Centro Absoluto) */}
      <section className="space-y-6 pt-4 border-t border-foreground/[0.03]">
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
            <div>
              <Button 
                variant="outline" 
                onClick={() => navigate('/reflection/today')}
                className="text-[10px] px-6 py-2.5 uppercase tracking-widest opacity-60 hover:opacity-100 transition-opacity"
              >
                Mergulhar na leitura
              </Button>
            </div>
          </div>
        )}
      </section>

      {/* Bloco 3: Palavra da Noite (Sessão Noturna Dinâmica) */}
      {isNight && nightData && (
        <section className="space-y-6 pt-12 border-t border-foreground/[0.03] animate-fade-in">
          <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-foreground/35">
            Palavra da Noite
          </p>
          <div className="bg-[#121613] p-8 rounded-lg border border-[#FAF8F5]/5 space-y-6 max-w-lg">
            <blockquote className="font-serif italic text-base text-[#FAF8F5]/90 leading-relaxed">
              “{nightData.share_quote}”
            </blockquote>
            <p className="text-[9px] uppercase tracking-[0.2em] font-serif italic text-foreground/45 text-right">
              — {nightData.scripture_reference}
            </p>
            <div className="w-8 h-[0.5px] bg-[#FAF8F5]/10 mx-auto my-4" />
            <div className="space-y-2">
              <p className="text-[9px] font-serif italic text-foreground/30 text-center tracking-widest">
                Oração de encerramento
              </p>
              <p className="font-serif text-sm text-[#FAF8F5]/65 italic leading-relaxed text-center max-w-sm mx-auto">
                {nightData.closing_prayer}
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Bloco 4: Do que seu coração precisa hoje? (Presença Emocional) */}
      <section className="space-y-6 pt-8 border-t border-foreground/[0.03]">
        <p className="text-[9px] font-medium uppercase tracking-[0.25em] text-foreground/35">
          Presença & Acolhimento
        </p>
        <div className="space-y-6">
          <div className="space-y-2">
            <h2 className="font-serif text-lg text-foreground/80 leading-snug">Do que seu coração precisa hoje?</h2>
            <p className="text-foreground/50 font-sans text-xs font-light max-w-md leading-relaxed">
              Parem por um instante. Escolham uma nuance de seu coração para receber um acolhimento pastoral sob medida.
            </p>
          </div>
          <div>
            <Button 
              variant="outline" 
              onClick={() => navigate('/devotional/emotions')}
              className="text-[10px] px-6 py-2.5 uppercase tracking-widest opacity-60 hover:opacity-100 transition-opacity"
            >
              Silenciar e escolher
            </Button>
          </div>
        </div>
      </section>

      {/* Bloco 5: Memória Espiritual / Observação Pastoral */}
      {journeyData && journeyData.journey_text && (
        <section className="space-y-4 pt-8 border-t border-foreground/[0.03] max-w-md animate-fade-in">
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
        <section className="space-y-6 pt-8 border-t border-foreground/[0.03]">
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
