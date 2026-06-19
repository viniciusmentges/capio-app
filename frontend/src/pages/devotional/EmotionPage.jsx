import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getEmotions, getDevotionalByEmotion } from '../../lib/devotional';
import EmotionSelector from '../../components/devotional/EmotionSelector';
import DevotionalResult from '../../components/devotional/DevotionalResult';
import LoadingState from '../../components/ui/LoadingState';
import OfflineState from '../../components/ui/OfflineState';
import PWAInstallPrompt from '../../components/layout/PWAInstallPrompt';
import PushOptInPrompt from '../../components/layout/PushOptInPrompt';
import Button from '../../components/ui/Button';
import TextSizeSelector from '../../components/ui/TextSizeSelector';
import localforage from 'localforage';
import {
  EditorialContainer,
  EditorialSection,
  EditorialTitle,
  EditorialSubtitle,
  EditorialLabel
} from '../../components/design-system/editorial';
import { saveOfflineItem, getLatestOfflineItem } from '../../pwa/offlineStorage';
import { OFFLINE_KEYS } from '../../pwa/offlineKeys';
import { ANALYTICS_EVENTS, CONTENT_TYPES } from '../../analytics/events';
import { captureEvent } from '../../analytics/posthogClient';
import { captureException } from '../../observability/sentry';

export default function EmotionPage() {
  const [selectedSlug, setSelectedSlug] = useState(null);
  const [devotional, setDevotional] = useState(null);
  const [cachedEmotions, setCachedEmotions] = useState(null);
  const [lastSavedDevotional, setLastSavedDevotional] = useState(null);
  const [showOfflineOption, setShowOfflineOption] = useState(false);
  const navigate = useNavigate();

  // Buscar lista de emoções da API
  const { data: emotions, isLoading: isEmotionsLoading, isError: isEmotionsError } = useQuery({
    queryKey: ['devotional', 'emotions'],
    queryFn: getEmotions,
    staleTime: 1000 * 60 * 60 * 24, // 24h
  });

  // Gerar novo devocional
  const mutation = useMutation({
    mutationFn: getDevotionalByEmotion,
    onSuccess: (data) => {
      setDevotional(data);
      captureEvent(ANALYTICS_EVENTS.DEVOTIONAL_COMPLETED, {
        emotion_slug: selectedSlug,
        content_id: data?.id,
        cached: Boolean(data?.cached),
      });
      // Salva no banco offline (micro biblioteca offline v1)
      saveOfflineItem(OFFLINE_KEYS.DEVOTIONALS, data)
        .catch(err => {
          console.error('Erro ao salvar devocional offline:', err);
          captureException(err, { tags: { area: 'offline_storage', content_type: CONTENT_TYPES.DEVOTIONAL } });
        });
      window.scrollTo({ top: 0, behavior: 'instant' });
    },
    onError: (error) => {
      captureException(error, {
        tags: { area: 'ai', action: 'devotional_by_emotion' },
        extra: { emotion_slug: selectedSlug },
      });
    },
  });

  // 1. Salvar lista de emoções em cache quando buscar com sucesso
  useEffect(() => {
    if (emotions && emotions.length > 0) {
      localforage.setItem('emotions_list', emotions)
        .catch(err => console.error('Erro ao salvar emoções offline:', err));
    }
  }, [emotions]);

  // 2. Carregar recursos locais (emoções e último devocional da micro biblioteca) se estiver sem rede
  useEffect(() => {
    // Carregar emoções salvas
    localforage.getItem('emotions_list')
      .then(saved => {
        if (saved) setCachedEmotions(saved);
      })
      .catch(err => console.error('Erro ao ler emoções do localForage:', err));

    // Carregar devocional mais recente gerado
    getLatestOfflineItem(OFFLINE_KEYS.DEVOTIONALS)
      .then(saved => {
        if (saved) setLastSavedDevotional(saved);
      })
      .catch(err => console.error('Erro ao ler último devocional do localForage:', err));
  }, []);

  // Monitorar se a mutação deu erro por estar offline e habilitar opção do último devocional
  useEffect(() => {
    if (mutation.isError && lastSavedDevotional) {
      console.warn('[CAPIO PWA] Falha de conexão física na API de geração de devocionais. Oferecendo reidratação contemplativa do último item do IndexedDB.');
      setShowOfflineOption(true);
    }
  }, [mutation.isError, lastSavedDevotional]);

  useEffect(() => {
    if (devotional) {
      localStorage.setItem('capio_devotional_completed', 'true');
    }
  }, [devotional]);

  const handleReceiveDevotional = () => {
    if (!selectedSlug) return;
    captureEvent(ANALYTICS_EVENTS.DEVOTIONAL_STARTED, {
      emotion_slug: selectedSlug,
    });
    mutation.mutate({ emotion: selectedSlug });
  };

  const handleEmotionSelect = (slug) => {
    setSelectedSlug(slug);
    captureEvent(ANALYTICS_EVENTS.EMOTION_SELECTED, {
      emotion_slug: slug,
    });
  };

  // Se der erro de carregamento das emoções e tivermos o cache das emoções, usamos o cache!
  const activeEmotions = emotions || cachedEmotions;
  const isEmotionsOffline = !emotions && !!cachedEmotions;

  if (isEmotionsLoading && !cachedEmotions) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <LoadingState message="Buscando sentimentos..." />
      </div>
    );
  }

  if (mutation.isPending) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <LoadingState message="Preparando seu devocional..." />
      </div>
    );
  }

  // Se der erro na geração E tivermos o último devocional gerado, oferecemos a leitura direta dele
  if (showOfflineOption && lastSavedDevotional) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh] safe-x text-center space-y-xl animate-fade-in">
        <div className="space-y-lg max-w-sm mx-auto">
          <EditorialTitle as="h2" className="text-2xl leading-tight">Conexão Interrompida</EditorialTitle>
          <EditorialSubtitle as="p">
            Não conseguimos nos conectar para gerar uma nova leitura. Deseja abrir a última Palavra guardada no seu coração?
          </EditorialSubtitle>
        </div>
        <div className="flex flex-col sm:flex-row justify-center items-center gap-6 max-w-xs mx-auto w-full">
          <Button
            onClick={() => {
              setDevotional(lastSavedDevotional);
              setShowOfflineOption(false);
              mutation.reset();
              captureEvent(ANALYTICS_EVENTS.OFFLINE_CONTENT_VIEWED, {
                content_type: CONTENT_TYPES.DEVOTIONAL,
                content_id: lastSavedDevotional?.id,
              });
            }}
            className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
          >
            Abrir último devocional
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              setShowOfflineOption(false);
              mutation.reset();
            }}
            className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
          >
            Voltar
          </Button>
        </div>
      </div>
    );
  }

  // Se der erro geral de rede e não tivermos dados locais sequer de emoções nem de devocional
  if (isEmotionsError && !activeEmotions && !lastSavedDevotional) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <OfflineState onRetry={() => window.location.reload()} />
      </div>
    );
  }

  // Se estiver completamente offline, mas temos o último devocional salvo, podemos dar a opção direta
  if (!navigator.onLine && !devotional && lastSavedDevotional) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh] safe-x text-center space-y-xl animate-fade-in">
        <div className="space-y-lg max-w-sm mx-auto">
          <div className="w-12 h-px bg-foreground/10 mx-auto mb-lg" />
          <EditorialTitle as="h2" className="text-2xl tracking-tight">Espaço Offline</EditorialTitle>
          <EditorialSubtitle as="p">
            Você está sem conexão de rede. Deseja meditar com a última leitura guardada no seu dispositivo?
          </EditorialSubtitle>
        </div>
        <div className="flex justify-center max-w-xs mx-auto w-full">
          <Button
            onClick={() => {
              setDevotional(lastSavedDevotional);
              captureEvent(ANALYTICS_EVENTS.OFFLINE_CONTENT_VIEWED, {
                content_type: CONTENT_TYPES.DEVOTIONAL,
                content_id: lastSavedDevotional?.id,
              });
            }}
            className="w-full py-4 text-[10px] uppercase tracking-[0.2em]"
          >
            Ler devocional salvo
          </Button>
        </div>
      </div>
    );
  }

  if (devotional) {
    const isLocalData = lastSavedDevotional && devotional.id === lastSavedDevotional.id && !navigator.onLine;
    return (
      <div className="">
        {isLocalData && (
          <div className="flex justify-center -mt-8 mb-8">
            <span className="font-sans text-[8px] uppercase tracking-[0.3em] bg-foreground/5 text-foreground/45 px-3 py-1 rounded-full animate-pulse">
              Leitura Guardada — Presença Offline
            </span>
          </div>
        )}
        <TextSizeSelector />
        <DevotionalResult devotional={devotional} />
        <PushOptInPrompt />
        <PWAInstallPrompt />
        <div className="flex justify-center pb-12">
          <Button 
            variant="outline" 
            onClick={() => {
              setDevotional(null);
              setSelectedSlug(null);
            }}
          >
            Escolher outra emoção
          </Button>
        </div>
      </div>
    );
  }

  return (
    <EditorialContainer className="pb-xl">
      <EditorialSection className="space-y-md text-center">
        {isEmotionsOffline && (
          <span className="font-sans text-[7px] uppercase tracking-[0.3em] bg-foreground/5 text-foreground/40 px-2 py-0.5 rounded-full inline-block mb-2">
            Modo Presença Offline
          </span>
        )}
        <EditorialTitle as="h1" className="text-3xl">Do que seu coração precisa hoje?</EditorialTitle>
        <EditorialSubtitle as="p">
          Escolha a emoção que mais se aproxima deste momento.
        </EditorialSubtitle>
      </EditorialSection>

      <EditorialSection className="max-w-md mx-auto w-full pt-0">
        <EmotionSelector 
          emotions={activeEmotions || []} 
          selectedSlug={selectedSlug}
          onSelect={handleEmotionSelect}
        />
      </EditorialSection>

      <EditorialSection className="pt-sm flex flex-col items-center space-y-md">
        <Button 
          onClick={handleReceiveDevotional}
          disabled={!selectedSlug}
          className="px-12 uppercase tracking-widest text-xs"
        >
          {navigator.onLine ? 'Receber devocional' : 'Gerar (Requer internet)'}
        </Button>

        <button 
          onClick={() => navigate('/bible/explain')}
          className="editorial-label opacity-70 hover:opacity-100 transition-opacity"
        >
          Ou busque uma passagem específica
        </button>
      </EditorialSection>
    </EditorialContainer>
  );
}
