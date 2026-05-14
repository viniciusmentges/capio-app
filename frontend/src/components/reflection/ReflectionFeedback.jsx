import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { respondTodayReflection } from '../../lib/reflection';
import Button from '../ui/Button';

export default function ReflectionFeedback({ reflectionId }) {
  const [submitted, setSubmitted] = useState(false);
  const [comment, setComment] = useState('');

  const mutation = useMutation({
    mutationFn: respondTodayReflection,
    onSuccess: () => {
      setSubmitted(true);
    },
    // Falhas podem ser engolidas ou gerar feedback sutil, 
    // mas priorizamos uma UX pacífica onde falha técnica não assusta o usuário.
  });

  if (submitted) {
    return (
      <div className="pt-12 pb-8 text-center animate-fade-in">
        <p className="font-serif text-foreground/50 tracking-wide">
          Obrigado por compartilhar este momento.
        </p>
      </div>
    );
  }

  const handleResponse = (helpful) => {
    mutation.mutate({ 
      reflection_id: reflectionId, 
      helpful, 
      comment 
    });
  };

  return (
    <div className="pt-12 pb-8 space-y-6">
      <div className="w-12 h-px bg-foreground/10 mx-auto" />
      
      <div className="space-y-6 text-center">
        <p className="font-serif text-lg text-foreground/80">
          Isso ajudou você hoje?
        </p>

        <div className="flex flex-col space-y-4 max-w-xs mx-auto">
          <div className="flex gap-4 justify-center">
            <Button 
              variant="outline" 
              className="flex-1"
              disabled={mutation.isPending}
              onClick={() => handleResponse(true)}
            >
              Sim
            </Button>
            <Button 
              variant="outline" 
              className="flex-1"
              disabled={mutation.isPending}
              onClick={() => handleResponse(false)}
            >
              Não
            </Button>
          </div>

          <input
            type="text"
            placeholder="Se quiser, escreva uma palavra sobre este momento."
            className="w-full px-4 py-3 bg-transparent border border-foreground/10 rounded-xl text-sm placeholder:text-foreground/30 focus:outline-none focus:border-foreground/30 transition-colors text-center"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            disabled={mutation.isPending}
          />
        </div>
      </div>
    </div>
  );
}
