import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api';
import ReflectionCard from '../../components/reflection/ReflectionCard';
import DevotionalResult from '../../components/devotional/DevotionalResult';
import BibleExplanationCard from '../../components/bible/BibleExplanationCard';
import LoadingState from '../../components/ui/LoadingState';
import ErrorState from '../../components/ui/ErrorState';
import Button from '../../components/ui/Button';

async function fetchPublicContent(type, id) {
  let endpoint = '';
  if (type === 'reflection') endpoint = `/api/reflection/public/${id}/`;
  else if (type === 'devotional') endpoint = `/api/devotional/public/${id}/`;
  else if (type === 'explanation') endpoint = `/api/bible/public/${id}/`;
  
  if (!endpoint) throw new Error('Tipo de conteúdo inválido');
  
  const { data } = await api.get(endpoint);
  return data;
}

export default function SharedContentViewer() {
  const { type, id } = useParams();

  const { data, isLoading, isError } = useQuery({
    queryKey: ['public-content', type, id],
    queryFn: () => fetchPublicContent(type, id),
    staleTime: 1000 * 60 * 60, // 1 hora
  });

  React.useEffect(() => {
    if (data) {
      const title = data.title || data.reference_display || 'Uma Palavra para você';
      document.title = `CAPIO — ${title}`;
    } else {
      document.title = 'CAPIO — Espaço Contemplativo';
    }
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <LoadingState message="Buscando esta Palavra..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <ErrorState message="Esta leitura não está mais disponível ou o link é inválido." />
        <div className="flex justify-center mt-12">
          <Link to="/">
            <Button variant="outline">Ir para a CAPIO</Button>
          </Link>
        </div>
      </div>
    );
  }

  const renderContent = () => {
    if (type === 'reflection') {
      return <ReflectionCard data={data} />;
    }
    if (type === 'devotional') {
      return <DevotionalResult devotional={data} />;
    }
    if (type === 'explanation') {
      return <BibleExplanationCard explanation={data} />;
    }
    return null;
  };

  return (
    <div className="min-h-screen pb-32">
      <div className="max-w-2xl mx-auto pt-12">
        {renderContent()}
        
        <div className="mt-20 px-6 text-center space-y-12">
          <div className="w-12 h-px bg-foreground/5 mx-auto" />
          <div className="space-y-6">
            <p className="text-sm font-sans font-light text-foreground/40 leading-relaxed italic">
              Esta é uma leitura compartilhada da CAPIO.
            </p>
            <Link to="/" className="inline-block">
              <Button variant="outline" className="text-[10px] uppercase tracking-[0.2em] px-8">
                Começar minha jornada na CAPIO
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
