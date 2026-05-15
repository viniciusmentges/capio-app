import React from 'react';
import { Link } from 'react-router-dom';
import ProgressiveReveal from '../../components/devotional/ProgressiveReveal';
import Button from '../../components/ui/Button';

export default function ForgotPasswordPage() {
  const supportUrl = import.meta.env.VITE_SUPPORT_CONTACT_URL;

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center px-6 pb-24">
      <div className="max-w-md mx-auto w-full space-y-16">
        
        <ProgressiveReveal delay={300}>
          <header className="text-center space-y-6">
            <h1 className="font-serif text-3xl text-foreground/40 italic">
              Recuperar Acesso
            </h1>
            <div className="w-8 h-px bg-foreground/5 mx-auto" />
          </header>
        </ProgressiveReveal>

        <ProgressiveReveal delay={800}>
          <div className="space-y-10">
            <p className="text-contemplative text-foreground/70 text-center leading-relaxed">
              A recuperação automática de senha ainda está sendo preparada. 
              Se você precisar de ajuda para acessar sua conta, entre em contato conosco.
            </p>
            
            {supportUrl && (
              <div className="flex justify-center pt-4">
                <a 
                  href={supportUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-block"
                >
                  <Button variant="outline" className="text-[10px] uppercase tracking-[0.2em] px-8">
                    Pedir ajuda
                  </Button>
                </a>
              </div>
            )}
          </div>
        </ProgressiveReveal>

        <ProgressiveReveal delay={1500}>
          <footer className="pt-12 text-center">
            <Link 
              to="/login" 
              className="text-[10px] font-serif italic text-foreground/30 hover:text-foreground/50 transition-colors uppercase tracking-[0.2em]"
            >
              Voltar para o login
            </Link>
          </footer>
        </ProgressiveReveal>

      </div>
    </div>
  );
}
