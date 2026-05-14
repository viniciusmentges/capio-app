import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getTodayReflection } from '../../lib/reflection';
import ReflectionCard from '../../components/reflection/ReflectionCard';
import ReflectionFeedback from '../../components/reflection/ReflectionFeedback';
import LoadingState from '../../components/ui/LoadingState';
import ErrorState from '../../components/ui/ErrorState';
import EmptyState from '../../components/ui/EmptyState';

export default function TodayReflectionPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['reflection', 'today'],
    queryFn: getTodayReflection,
    staleTime: 1000 * 60 * 60, // 1 hora de cache
  });

  if (isLoading) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <LoadingState message="Carregando a reflexão de hoje..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <ErrorState message="A reflexão de hoje não está disponível no momento." />
      </div>
    );
  }

  if (!data || !data.reflection) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <EmptyState message="A reflexão de hoje ainda não está disponível. Volte em alguns instantes." />
      </div>
    );
  }

  return (
    <div className="pb-12 space-y-12">
      <ReflectionCard data={data.reflection} />
      <ReflectionFeedback reflectionId={data.reflection.id} />
    </div>
  );
}
