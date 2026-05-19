import React from 'react';

export default function EditorialSkeleton() {
  return (
    <div className="w-full space-y-16 animate-fade-in py-8">
      {/* 1. Wordmark/Categoria sutil */}
      <div className="space-y-4 flex flex-col items-center">
        <div className="h-2 w-16 bg-foreground/[0.04] rounded-sm animate-pulse-slow" />
        <div className="h-4 w-40 bg-foreground/[0.03] rounded-sm animate-pulse-slow delay-100" />
      </div>

      {/* 2. Conteúdo de leitura (Linhas editoriais minimalistas em pulso de respiração) */}
      <div className="space-y-6 max-w-md mx-auto pt-8">
        <div className="h-3 w-[90%] bg-foreground/[0.03] rounded-sm mx-auto animate-pulse-slow delay-200" />
        <div className="h-3 w-[85%] bg-foreground/[0.03] rounded-sm mx-auto animate-pulse-slow delay-300" />
        <div className="h-3 w-[95%] bg-foreground/[0.03] rounded-sm mx-auto animate-pulse-slow delay-400" />
        <div className="h-3 w-[80%] bg-foreground/[0.03] rounded-sm mx-auto animate-pulse-slow delay-500" />
      </div>

      {/* 3. Ação inferior */}
      <div className="flex justify-center pt-12">
        <div className="h-10 w-32 bg-foreground/[0.03] rounded-sm animate-pulse-slow delay-600" />
      </div>

      <style>{`
        .animate-pulse-slow {
          animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse-slow {
          0%, 100% { opacity: .4; }
          50% { opacity: .9; }
        }
      `}</style>
    </div>
  );
}
