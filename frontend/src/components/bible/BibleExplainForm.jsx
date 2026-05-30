import React, { useState } from 'react';
import Input from '../ui/Input';
import Button from '../ui/Button';

export default function BibleExplainForm({ onSubmit, isLoading, serverError }) {
  const [passage, setPassage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!passage.trim()) return;
    
    // Validação UX leve
    if (passage.length > 50) {
       // Just to prevent very large texts, but server handles real validation
    }
    
    onSubmit(passage);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 max-w-md mx-auto w-full">
      <div className="space-y-2">
        <Input
          placeholder="Ex: Salmo 23, João 3:16, Romanos 8"
          value={passage}
          onChange={(e) => setPassage(e.target.value)}
          disabled={isLoading}
          className="text-center"
        />
        {serverError && (
          <p className="text-xs text-foreground/60 text-center font-serif italic px-4 animate-fade-in">
            {serverError}
          </p>
        )}
      </div>
      <div className="flex justify-center">
        <Button disabled={isLoading || !passage.trim()}>
          Explicar passagem
        </Button>
      </div>
    </form>
  );
}
