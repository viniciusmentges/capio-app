import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getTodayReflection } from '../../lib/reflection';
import ReflectionCard from '../../components/reflection/ReflectionCard';
import ReflectionFeedback from '../../components/reflection/ReflectionFeedback';
import LoadingState from '../../components/ui/LoadingState';
import OfflineState from '../../components/ui/OfflineState';
import PWAInstallPrompt from '../../components/layout/PWAInstallPrompt';
import PushOptInPrompt from '../../components/layout/PushOptInPrompt';
import { saveOfflineItem, getLatestOfflineItem } from '../../pwa/offlineStorage';
import { OFFLINE_KEYS } from '../../pwa/offlineKeys';

export default function TodayReflectionPage() {
  const [offlineData, setOfflineData] = useState(null);
  const [loadingOffline, setLoadingOffline] = useState(true);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['reflection', 'today'],
    queryFn: getTodayReflection,
    staleTime: 1000 * 60 * 60, // 1 hora de cache
  });

  // Salvar a reflexão diária com sucesso na micro biblioteca offline
  useEffect(() => {
    if (data?.reflection) {
      saveOfflineItem(OFFLINE_KEYS.DAILY_REFLECTIONS, data.reflection)
        .catch(err => console.error('Erro ao salvar reflexão offline:', err));
    }
  }, [data]);

  // Carregar dados offline do storage unificado se a rede falhar
  useEffect(() => {
    if (isError || (!isLoading && !data?.reflection)) {
      setLoadingOffline(true);
      getLatestOfflineItem(OFFLINE_KEYS.DAILY_REFLECTIONS)
        .then(saved => {
          setOfflineData(saved);
        })
        .catch(err => {
          console.error('Erro ao recuperar reflexão offline:', err);
        })
        .finally(() => {
          setLoadingOffline(false);
        });
    } else {
      setLoadingOffline(false);
    }
  }, [isError, isLoading, data]);

  // Resiliência offline: Se der erro na rede, mas houver dado salvo localmente
  const activeReflection = data?.reflection || offlineData;
  const isOfflineMode = !data?.reflection && !!offlineData;

  useEffect(() => {
    if (activeReflection) {
      localStorage.setItem('capio_reflection_viewed', 'true');
    }
  }, [activeReflection]);

  if (isLoading || (loadingOffline && isError)) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <LoadingState message="Carregando a reflexão de hoje..." />
      </div>
    );
  }

  if (isOfflineMode && activeReflection) {
    return (
      <div className="pb-12 space-y-12">
        <div className="flex justify-center -mt-8">
          <span className="font-sans text-[8px] uppercase tracking-[0.3em] bg-foreground/5 text-foreground/45 px-3 py-1 rounded-full animate-pulse">
            Espaço Offline — Presença Preservada
          </span>
        </div>
        <ReflectionCard data={activeReflection} />
        <div className="text-center font-serif italic text-xs text-foreground/20 pt-4">
          Você está em espaço de recolhimento offline. Esta leitura foi guardada em seu dispositivo.
        </div>
      </div>
    );
  }

  // Se der erro na rede e não tivermos nenhuma reflexão salva no dispositivo
  if (isError && !activeReflection) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <OfflineState onRetry={() => refetch()} />
      </div>
    );
  }

  if (!activeReflection) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <OfflineState onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div className="pb-12 space-y-12">
      <ReflectionCard data={activeReflection} />
      <ReflectionFeedback reflectionId={activeReflection.id} />
      <PushOptInPrompt />
      <PWAInstallPrompt />
    </div>
  );
}
