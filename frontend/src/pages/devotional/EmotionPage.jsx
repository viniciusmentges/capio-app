import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getEmotions, getDevotionalByEmotion } from '../../lib/devotional';
import EmotionSelector from '../../components/devotional/EmotionSelector';
import DevotionalResult from '../../components/devotional/DevotionalResult';
import LoadingState from '../../components/ui/LoadingState';
import ErrorState from '../../components/ui/ErrorState';
import Button from '../../components/ui/Button';

export default function EmotionPage() {
  const [selectedSlug, setSelectedSlug] = useState(null);
  const [devotional, setDevotional] = useState(null);

  const { data: emotions, isLoading: isEmotionsLoading, isError: isEmotionsError } = useQuery({
    queryKey: ['devotional', 'emotions'],
    queryFn: getEmotions,
    staleTime: 1000 * 60 * 60 * 24, // 24h
  });

  const mutation = useMutation({
    mutationFn: getDevotionalByEmotion,
    onSuccess: (data) => {
      setDevotional(data);
      window.scrollTo({ top: 0, behavior: 'instant' });
    },
  });

  const handleReceiveDevotional = () => {
    if (!selectedSlug) return;
    mutation.mutate({ emotion: selectedSlug });
  };

  if (isEmotionsLoading || mutation.isPending) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <LoadingState 
          message={mutation.isPending ? "Preparando seu devocional..." : "Buscando sentimentos..."} 
        />
      </div>
    );
  }

  if (isEmotionsError || mutation.isError) {
    return (
      <div className="flex flex-col justify-center min-h-[100dvh]">
        <ErrorState message="Não foi possível preparar seu devocional agora." />
      </div>
    );
  }

  if (devotional) {
    return (
    <div className="">
        <DevotionalResult devotional={devotional} />
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
    <div className="space-y-[var(--space-section)] pb-12">
      <header className="space-y-6 text-center">
        <h1 className="font-serif text-3xl text-foreground leading-tight">Do que seu coração precisa hoje?</h1>
        <p className="text-foreground/40 font-sans font-light tracking-wide text-xs">
          Escolha a emoção que mais se aproxima deste momento.
        </p>
      </header>

      <div className="max-w-md mx-auto w-full">
        <EmotionSelector 
          emotions={emotions || []} 
          selectedSlug={selectedSlug}
          onSelect={setSelectedSlug}
        />
      </div>

      <div className="pt-4 flex justify-center">
        <Button 
          onClick={handleReceiveDevotional}
          disabled={!selectedSlug}
          className="px-12 uppercase tracking-widest text-xs"
        >
          Receber devocional
        </Button>
      </div>
    </div>
  );
}
