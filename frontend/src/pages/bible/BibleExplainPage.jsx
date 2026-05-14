import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { explainBiblePassage } from '../../lib/bible';
import BibleExplainForm from '../../components/bible/BibleExplainForm';
import BibleExplanationCard from '../../components/bible/BibleExplanationCard';
import LoadingState from '../../components/ui/LoadingState';
import ErrorState from '../../components/ui/ErrorState';
import Button from '../../components/ui/Button';

export default function BibleExplainPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const referenceParam = searchParams.get('ref');

  // Query para buscar/reidratar se houver ref na URL
  const { data: explanation, isLoading, isError, error } = useQuery({
    queryKey: ['bible-explain', referenceParam],
    queryFn: () => explainBiblePassage({ reference: referenceParam }),
    enabled: !!referenceParam,
    staleTime: 1000 * 60 * 30, // 30 minutos
    gcTime: 1000 * 60 * 60, // 1 hora
  });

  const mutation = useMutation({
    mutationFn: explainBiblePassage,
    onSuccess: (data) => {
      // Quando a mutação termina, atualizamos a URL para persistir
      setSearchParams({ ref: data.reference_display || data.passage });
      // Também alimentamos o cache do useQuery manualmente para evitar refetch
      queryClient.setQueryData(['bible-explain', data.reference_display || data.passage], data);
      window.scrollTo({ top: 0, behavior: 'instant' });
    },
  });

  const handleExplain = (passage) => {
    mutation.mutate({ passage });
  };

  const handleReset = () => {
    setSearchParams({});
    queryClient.invalidateQueries({ queryKey: ['bible-explain'] });
  };

  if (mutation.isPending || (isLoading && referenceParam)) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <LoadingState message="Preparando sua leitura..." />
      </div>
    );
  }

  if (mutation.isError || (isError && referenceParam)) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <ErrorState message="Não foi possível preparar esta leitura agora." />
        <div className="flex justify-center mt-8">
          <Button variant="outline" onClick={handleReset}>Voltar</Button>
        </div>
      </div>
    );
  }

  if (explanation) {
    return (
      <div className="animate-fade-in">
        <BibleExplanationCard explanation={explanation} />
        <div className="flex justify-center pb-12 pt-8">
          <Button 
            variant="outline" 
            onClick={handleReset}
            className="text-[10px] opacity-40 hover:opacity-100 transition-opacity uppercase tracking-[0.2em]"
          >
            Explicar outra passagem
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-[var(--space-section)] pb-12 animate-fade-in">
      <header className="space-y-6 text-center">
        <h1 className="font-serif text-3xl text-foreground leading-tight">
          Qual passagem você gostaria de compreender hoje?
        </h1>
        <p className="text-foreground/40 font-sans font-light tracking-wide text-xs">
          Digite um versículo, capítulo ou passagem bíblica.
        </p>
      </header>

      <BibleExplainForm 
        onSubmit={handleExplain} 
        isLoading={mutation.isPending} 
      />
    </div>
  );
}

