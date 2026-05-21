import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { explainBiblePassage } from '../../lib/bible';
import BibleExplainForm from '../../components/bible/BibleExplainForm';
import BibleExplanationCard from '../../components/bible/BibleExplanationCard';
import LoadingState from '../../components/ui/LoadingState';
import OfflineState from '../../components/ui/OfflineState';
import Button from '../../components/ui/Button';
import TextSizeSelector from '../../components/ui/TextSizeSelector';
import { saveOfflineItem, getLatestOfflineItem } from '../../pwa/offlineStorage';
import { OFFLINE_KEYS } from '../../pwa/offlineKeys';
import { ANALYTICS_EVENTS, CONTENT_TYPES } from '../../analytics/events';
import { captureEvent } from '../../analytics/posthogClient';
import { captureException } from '../../observability/sentry';

export default function BibleExplainPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const referenceParam = searchParams.get('ref');

  const [localExplanation, setLocalExplanation] = useState(null);
  const [lastSavedExplanation, setLastSavedExplanation] = useState(null);
  const [showOfflineOption, setShowOfflineOption] = useState(false);

  const { data: explanation, isLoading, isError, refetch } = useQuery({
    queryKey: ['bible-explain', referenceParam],
    queryFn: () => explainBiblePassage({ reference: referenceParam }),
    enabled: !!referenceParam,
    staleTime: 1000 * 60 * 30,
    gcTime: 1000 * 60 * 60,
  });

  const mutation = useMutation({
    mutationFn: explainBiblePassage,
    onSuccess: (data) => {
      saveOfflineItem(OFFLINE_KEYS.BIBLE_EXPLANATIONS, data)
        .catch(err => {
          console.error('Erro ao salvar explicacao biblica offline:', err);
          captureException(err, { tags: { area: 'offline_storage', content_type: CONTENT_TYPES.BIBLE_EXPLANATION } });
        });

      setSearchParams({ ref: data.reference_display || data.passage });
      queryClient.setQueryData(['bible-explain', data.reference_display || data.passage], data);
      window.scrollTo({ top: 0, behavior: 'instant' });
    },
    onError: (error) => {
      captureException(error, {
        tags: { area: 'ai', action: 'bible_explanation' },
      });
    },
  });

  useEffect(() => {
    if (explanation) {
      saveOfflineItem(OFFLINE_KEYS.BIBLE_EXPLANATIONS, explanation)
        .catch(err => {
          console.error('Erro ao salvar explicacao biblica offline:', err);
          captureException(err, { tags: { area: 'offline_storage', content_type: CONTENT_TYPES.BIBLE_EXPLANATION } });
        });
    }
  }, [explanation]);

  useEffect(() => {
    getLatestOfflineItem(OFFLINE_KEYS.BIBLE_EXPLANATIONS)
      .then(saved => {
        if (saved) setLastSavedExplanation(saved);
      })
      .catch(err => {
        console.error('Erro ao obter explicacao biblica offline:', err);
        captureException(err, { tags: { area: 'offline_storage', action: 'read_latest_bible_explanation' } });
      });
  }, []);

  useEffect(() => {
    if ((mutation.isError || isError) && lastSavedExplanation) {
      console.warn('[CAPIO PWA] Falha de conexao fisica na API de exegese biblica. Oferecendo reidratacao contemplativa da ultima explicacao do IndexedDB.');
      setShowOfflineOption(true);
    }
  }, [mutation.isError, isError, lastSavedExplanation]);

  const handleExplain = (passage) => {
    captureEvent(ANALYTICS_EVENTS.BIBLE_EXPLANATION_REQUESTED, {
      has_reference: Boolean(passage),
    });
    mutation.mutate({ passage });
  };

  const handleReset = () => {
    setSearchParams({});
    setLocalExplanation(null);
    queryClient.invalidateQueries({ queryKey: ['bible-explain'] });
  };

  const openSavedExplanation = () => {
    setLocalExplanation(lastSavedExplanation);
    captureEvent(ANALYTICS_EVENTS.OFFLINE_CONTENT_VIEWED, {
      content_type: CONTENT_TYPES.BIBLE_EXPLANATION,
      content_id: lastSavedExplanation?.id,
    });
  };

  if (mutation.isPending || (isLoading && referenceParam)) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <LoadingState message="Preparando sua leitura..." />
      </div>
    );
  }

  if (showOfflineOption && lastSavedExplanation) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh] px-6 text-center space-y-12 animate-fade-in">
        <div className="space-y-6 max-w-sm mx-auto">
          <h2 className="font-serif text-2xl text-foreground/80 leading-tight">Conexao interrompida</h2>
          <p className="font-serif italic text-sm text-foreground/45 leading-relaxed">
            Nao conseguimos nos conectar para explicar esta passagem. Deseja abrir a ultima Palavra guardada no seu coracao?
          </p>
        </div>
        <div className="flex flex-col sm:flex-row justify-center items-center gap-6 max-w-xs mx-auto w-full">
          <Button
            onClick={() => {
              openSavedExplanation();
              setShowOfflineOption(false);
              mutation.reset();
            }}
            className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
          >
            Abrir ultima leitura
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              setShowOfflineOption(false);
              mutation.reset();
              handleReset();
            }}
            className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
          >
            Voltar
          </Button>
        </div>
      </div>
    );
  }

  if (!navigator.onLine && !explanation && !localExplanation && lastSavedExplanation) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh] px-6 text-center space-y-16 animate-fade-in">
        <div className="space-y-6 max-w-sm mx-auto">
          <div className="w-12 h-px bg-foreground/10 mx-auto mb-6" />
          <h2 className="font-serif text-2xl text-foreground/80 tracking-tight">Espaco Offline</h2>
          <p className="font-serif italic text-sm text-foreground/45 leading-relaxed">
            Voce esta sem conexao de rede. Deseja ler a ultima explicacao biblica guardada no seu dispositivo?
          </p>
        </div>
        <div className="flex justify-center max-w-xs mx-auto w-full">
          <Button
            onClick={openSavedExplanation}
            className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
          >
            Ler explicacao salva
          </Button>
        </div>
      </div>
    );
  }

  const activeExplanation = explanation || localExplanation;
  const isGeneralOffline = !navigator.onLine && !activeExplanation && !lastSavedExplanation;

  if (isGeneralOffline || ((mutation.isError || isError) && !lastSavedExplanation)) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <OfflineState onRetry={() => refetch()} />
      </div>
    );
  }

  if (activeExplanation) {
    const isLocalData = localExplanation && !navigator.onLine;
    return (
      <div className="animate-fade-in">
        {isLocalData && (
          <div className="flex justify-center -mt-8 mb-8">
            <span className="font-sans text-[8px] uppercase tracking-[0.3em] bg-foreground/5 text-foreground/45 px-3 py-1 rounded-full animate-pulse">
              Leitura Guardada - Presenca Offline
            </span>
          </div>
        )}
        <TextSizeSelector />
        <BibleExplanationCard explanation={activeExplanation} />
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
        {!navigator.onLine && (
          <span className="font-sans text-[7px] uppercase tracking-[0.3em] bg-foreground/5 text-foreground/40 px-2 py-0.5 rounded-full inline-block mb-2">
            Modo Presenca Offline
          </span>
        )}
        <h1 className="font-serif text-3xl text-foreground leading-tight">
          Qual passagem voce gostaria de compreender hoje?
        </h1>
        <p className="text-foreground/40 font-sans font-light tracking-wide text-xs">
          Digite um versiculo, capitulo ou passagem biblica.
        </p>
      </header>

      <BibleExplainForm
        onSubmit={handleExplain}
        isLoading={mutation.isPending}
      />
    </div>
  );
}
