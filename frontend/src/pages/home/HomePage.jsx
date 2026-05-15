import React from 'react';
import { useNavigate, Link } from 'react-router-dom';

import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../hooks/useAuth';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import { getGreetingContext, formatFirstName } from '../../utils/greeting';
import { getTodayReflection } from '../../lib/reflection';

export default function HomePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const { data: reflection, isLoading: isReflectionLoading } = useQuery({
    queryKey: ['reflection', 'today'],
    queryFn: getTodayReflection,
    staleTime: 1000 * 60 * 60,
  });

  const greeting = getGreetingContext();
  const firstName = formatFirstName(user);
  const title = firstName ? `${greeting}, ${firstName}.` : `${greeting}.`;

  const getReflectionPreview = () => {
    if (isReflectionLoading) return "Preparando sua reflexão...";
    if (!reflection || !reflection.reflection) return "A reflexão de hoje será preparada em instantes.";
    
    return reflection.reflection.reflection_body || reflection.reflection.title || "";
  };

  return (
    <div className="space-y-[var(--space-section)] animate-fade-in">
      
      {/* Bloco 1: Saudação Contextual */}
      <section className="space-y-6">
        <h1 className="text-3xl font-serif text-foreground tracking-tight">
          {title}
        </h1>
        <p className="text-foreground/40 font-sans font-light tracking-wide text-xs">
          Que este momento seja vivido com calma.
        </p>
      </section>

      {/* Bloco de Apoio - Discreto e Contextual */}
      <section className="animate-fade-in" style={{ animationDelay: '1000ms' }}>
        <div className="space-y-4">
          <p className="text-[10px] font-sans font-light text-foreground/40 leading-relaxed max-w-xs">
            A CAPIO é gratuita. Se este espaço tem feito bem a você, considere ajudar a mantê-lo vivo.
          </p>
          <Link 
            to="/apoie" 
            className="inline-block text-[10px] uppercase tracking-[0.2em] text-foreground/50 hover:text-foreground/80 underline underline-offset-4 decoration-foreground/10 transition-colors"
          >
            Ajudar a causa
          </Link>
        </div>
      </section>


      {/* Bloco 2: Reflexão de Hoje */}
      <section className="space-y-8">
        <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-foreground/30">
          Reflexão
        </p>
        <div className="space-y-10">
          <p className="text-2xl text-foreground/90 font-serif leading-relaxed">
            {getReflectionPreview()}
          </p>
          <div>
            <Button 
              variant="outline" 
              onClick={() => navigate('/reflection/today')}
              className="text-xs px-8 py-3 uppercase tracking-widest opacity-60 hover:opacity-100"
              disabled={isReflectionLoading}
            >
              Ler reflexão
            </Button>
          </div>
        </div>
      </section>

      {/* Bloco 3: Devocional por Emoção */}
      <section className="space-y-8">
        <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-foreground/30">
          Presença
        </p>
        <div className="space-y-10">
          <div className="space-y-4">
            <h2 className="font-serif text-2xl text-foreground">Do que seu coração precisa hoje?</h2>
            <p className="text-foreground/50 font-sans text-sm font-light">
              Escolha uma emoção e receba um acolhimento para este momento.
            </p>
          </div>
          <div>
            <Button 
              variant="outline" 
              onClick={() => navigate('/devotional/emotions')}
              className="text-xs px-8 py-3 uppercase tracking-widest opacity-60 hover:opacity-100"
            >
              Iniciar
            </Button>
          </div>
        </div>
      </section>
      {/* Bloco de Rodapé - Discreto e Contemplativo */}
      <footer className="pt-24 space-y-16 pb-12">
        <div className="w-1 h-1 bg-foreground/10 rounded-full mx-auto" />
        
        <div className="flex flex-col items-center space-y-12">
          <Link 
            to="/apoie"
            className="text-[10px] uppercase tracking-[0.2em] text-foreground/30 hover:text-foreground/50 transition-colors"
          >
            Apoie a CAPIO
          </Link>

          <button 
            onClick={logout}
            className="text-[10px] uppercase tracking-[0.2em] text-foreground/10 hover:text-foreground/30 transition-colors"
          >
            Sair da conta
          </button>
        </div>
      </footer>


    </div>
  );
}
