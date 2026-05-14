import React, { useState } from 'react';
import Input from '../ui/Input';
import Button from '../ui/Button';

export default function BibleExplainForm({ onSubmit, isLoading }) {
  const [passage, setPassage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!passage.trim()) return;
    onSubmit(passage);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 max-w-md mx-auto w-full">
      <Input
        placeholder="Ex: Salmo 23, João 3:16, Romanos 8"
        value={passage}
        onChange={(e) => setPassage(e.target.value)}
        disabled={isLoading}
        className="text-center"
      />
      <div className="flex justify-center">
        <Button disabled={isLoading || !passage.trim()}>
          Explicar passagem
        </Button>
      </div>
    </form>
  );
}
