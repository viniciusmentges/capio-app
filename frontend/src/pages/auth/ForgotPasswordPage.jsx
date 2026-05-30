import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ProgressiveReveal from '../../components/devotional/ProgressiveReveal';
import Button from '../../components/ui/Button';
import { api } from '../../lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;
    
    setIsSubmitting(true);
    setMessage('');
    
    try {
      await api.post('/api/auth/password-reset/', { email });
      // Always show generic success message
      setMessage('Se este e-mail estiver cadastrado, enviaremos instruções para redefinir sua senha.');
    } catch (error) {
      // Even on error we should probably show generic message to prevent enumeration,
      // but let's be safe and show it.
      setMessage('Se este e-mail estiver cadastrado, enviaremos instruções para redefinir sua senha.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div 
      className="min-h-[100dvh] bg-background flex flex-col justify-center px-6 overflow-y-auto"
      style={{
        paddingTop: 'calc(2rem + env(safe-area-inset-top, 24px))',
        paddingBottom: 'calc(2rem + env(safe-area-inset-bottom, 24px))',
      }}
    >
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
              Informe o e-mail associado à sua conta.
            </p>
            
            {message ? (
              <div className="text-center bg-foreground/5 p-6 rounded-md">
                <p className="text-sm font-sans text-foreground/80 leading-relaxed">
                  {message}
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <label htmlFor="email" className="block text-[10px] uppercase tracking-[0.2em] font-sans text-foreground/50 ml-1">
                    E-mail
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-transparent border-b border-foreground/10 px-1 py-3 text-sm font-sans text-foreground/80 focus:outline-none focus:border-foreground/30 transition-colors placeholder:text-foreground/20"
                    placeholder="seu@email.com"
                  />
                </div>
                
                <div className="pt-4">
                  <Button 
                    type="submit" 
                    variant="outline" 
                    className="w-full text-[10px] uppercase tracking-[0.2em] py-4"
                    disabled={isSubmitting || !email}
                  >
                    {isSubmitting ? 'Enviando...' : 'Enviar instruções'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </ProgressiveReveal>

        <ProgressiveReveal delay={1000}>
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
