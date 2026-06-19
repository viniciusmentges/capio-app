import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  EditorialContainer,
  EditorialSection,
  EditorialCard,
  EditorialTitle,
  EditorialSubtitle,
  EditorialLabel,
  EditorialDivider
} from '../../components/design-system/editorial';
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
    <EditorialContainer className={`space-y-md animate-fade-in ${isNight ? 'capio-night-theme' : ''}`}>
      
      {/* Bloco 1: Saudação Contextual e Contemplativa */}
      <EditorialSection className="pt-sm space-y-sm">
        <EditorialTitle as="h1" className="text-3xl tracking-tight">
          {title}
        </EditorialTitle>
        <p className="editorial-subtitle">
          {isNight 
            ? "Encontre repouso e silêncio ao fechar este dia." 
            : "Que este momento seja vivido com calma e atenção plena."
          }
        </p>
      </EditorialSection>

      {/* Bloco 2: Devocional (Card de Papel) */}
      <EditorialSection>
        <EditorialCard 
          onClick={() => navigate('/devotional/emotions')}
          className="relative overflow-hidden flex flex-col space-y-sm cursor-pointer transition-all hover:opacity-90 group"
          role="button"
          tabIndex={0}
          onKeyDown={(e) => { if (e.key === 'Enter') navigate('/devotional/emotions') }}
        >
          <EditorialLabel>
            Devocional
          </EditorialLabel>
          <div className="space-y-xs z-10 relative">
            <h2 className="editorial-title text-xl">
              Como está seu coração hoje?
            </h2>
            <p className="editorial-subtitle max-w-[85%]">
              Escolha uma emoção e receba um devocional preparado para este momento.
            </p>
          </div>
          <div className="pt-xs z-10 relative">
            <span className="editorial-label underline underline-offset-8 decoration-accent/20 group-hover:decoration-accent/50">
              Silenciar e escolher
            </span>
          </div>
        </EditorialCard>
      </EditorialSection>

      {/* Bloco 3: Reflexão de Hoje (O Centro Absoluto) */}
      <EditorialSection className="border-t border-border pt-md space-y-sm">
        <EditorialLabel>
          Reflexão do Dia
        </EditorialLabel>
        {isReflectionLoading ? (
          <div className="py-md space-y-sm animate-pulse">
            <div className="h-4 bg-foreground/5 rounded w-3/4"></div>
            <div className="h-4 bg-foreground/5 rounded w-5/6"></div>
            <div className="h-4 bg-foreground/5 rounded w-2/3"></div>
            <p className="editorial-subtitle pt-xs">
              A leitura de hoje aguarda em silêncio...
            </p>
          </div>
        ) : (
          <div className="space-y-md">
            <h2 className="editorial-title text-xl opacity-75">
              {reflectionData?.reflection?.title || "Algo reservado para este dia"}
            </h2>
            <p className="editorial-body line-clamp-4">
              {getReflectionPreview()}
            </p>
            <div className="pt-xs">
              <button 
                onClick={() => navigate('/reflection/today')}
                className="editorial-label underline underline-offset-8 decoration-accent/20 hover:decoration-accent/50 py-sm cursor-pointer"
              >
                Mergulhar na leitura
              </button>
            </div>
          </div>
        )}
      </EditorialSection>

      {/* Bloco 4: Palavra da Noite (Sessão Noturna Dinâmica) */}
      {isNight && nightData && nightData.night_word && (
        <EditorialSection className="border-t border-border pt-md max-w-lg space-y-md">
          <EditorialLabel>
            Palavra da Noite
          </EditorialLabel>
          <div className="space-y-sm">
            <blockquote className="editorial-title text-lg opacity-80">
              “{nightData.night_word}”
            </blockquote>
            <EditorialLabel className="opacity-45 lowercase">
              — {nightData.scripture_reference}
            </EditorialLabel>
            <div className="space-y-xs pt-md border-t border-border">
              <EditorialLabel>
                Oração de encerramento
              </EditorialLabel>
              <p className="editorial-subtitle opacity-60">
                {nightData.night_prayer}
              </p>
            </div>
          </div>
        </EditorialSection>
      )}

      {/* Bloco 5: Memória Espiritual / Observação Pastoral */}
      {journeyData && journeyData.show_journey && journeyData.journey_text && (
        <EditorialSection className="border-t border-border pt-md max-w-md space-y-xs">
          <EditorialLabel>
            Observação Pastoral
          </EditorialLabel>
          <p className="editorial-subtitle opacity-55">
            "{journeyData.journey_text}"
          </p>
        </EditorialSection>
      )}

      {/* Bloco 6: Diário Litúrgico (Arquivo Silencioso) */}
      {archiveData && archiveData.length > 1 && (
        <EditorialSection className="border-t border-border pt-md space-y-sm">
          <EditorialLabel>
            Diário Litúrgico
          </EditorialLabel>
          <div className="space-y-sm max-w-md">
            {archiveData.slice(1, 4).map((ref, idx) => {
              const label = idx === 0 ? "Ontem" : idx === 1 ? "Anteontem" : "Esta semana";
              return (
                <div key={ref.id} className="flex justify-between items-center py-xs border-b border-border">
                  <div className="space-y-1">
                    <span className="editorial-label opacity-30">
                      {label}
                    </span>
                    <p className="editorial-subtitle text-foreground/75 opacity-100">
                      {ref.title}
                    </p>
                  </div>
                  <Link 
                    to={`/share/reflection/${ref.id}`} 
                    className="editorial-label underline decoration-accent/20 hover:decoration-accent/50"
                  >
                    Revisitar
                  </Link>
                </div>
              );
            })}
          </div>
        </EditorialSection>
      )}

      {/* Bloco de Apoio - Discreto e Contextual */}
      <EditorialSection className="border-t border-border pt-lg">
        <div className="space-y-xs">
          <p className="editorial-subtitle opacity-35 max-w-xs">
            A CAPIO é mantida por quem a utiliza de forma totalmente voluntária. Considere apoiar o projeto.
          </p>
          <Link 
            to="/apoie" 
            className="inline-block editorial-label underline underline-offset-4 decoration-accent/20 hover:decoration-accent/50"
          >
            Ajudar a causa
          </Link>
        </div>
      </EditorialSection>

      {/* Bloco de Rodapé - Discreto e Contemplativo */}
      <footer className="pt-xl space-y-lg">
        <EditorialDivider variant="dot" />
        
        <div className="flex flex-col items-center space-y-sm">
          <button 
            onClick={logout}
            className="editorial-label text-foreground/20 hover:text-foreground/40 transition-colors"
          >
            Sair da conta
          </button>
        </div>
      </footer>

    </EditorialContainer>
  );
}
