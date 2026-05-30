import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import ProgressiveReveal from '../../components/devotional/ProgressiveReveal';
import Button from '../../components/ui/Button';
import { api } from '../../lib/api';

export default function ResetPasswordConfirmPage() {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (newPassword !== confirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }
    
    if (newPassword.length < 8) {
      setError('A senha deve ter pelo menos 8 caracteres.');
      return;
    }

    setIsSubmitting(true);
    
    try {
      await api.post('/api/auth/password-reset/confirm/', {
        uid,
        token,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      setSuccess(true);
    } catch (err) {
      const errorMsg = err.response?.data?.token?.[0] 
        || err.response?.data?.new_password?.[0]
        || err.response?.data?.error 
        || 'Ocorreu um erro ao redefinir a senha. O link pode ter expirado.';
      setError(errorMsg);
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
              Nova Senha
            </h1>
            <div className="w-8 h-px bg-foreground/5 mx-auto" />
          </header>
        </ProgressiveReveal>

        <ProgressiveReveal delay={800}>
          <div className="space-y-10">
            {success ? (
              <div className="text-center space-y-8">
                <p className="text-sm font-sans text-foreground/80 leading-relaxed">
                  Sua senha foi redefinida com sucesso.
                </p>
                <Button 
                  onClick={() => navigate('/login')}
                  variant="outline" 
                  className="w-full text-[10px] uppercase tracking-[0.2em] py-4"
                >
                  Fazer Login
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 p-4 rounded text-center">
                    <p className="text-xs text-red-400 font-sans">{error}</p>
                  </div>
                )}
                
                <div className="space-y-2">
                  <label className="block text-[10px] uppercase tracking-[0.2em] font-sans text-foreground/50 ml-1">
                    Nova Senha
                  </label>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full bg-transparent border-b border-foreground/10 px-1 py-3 text-sm font-sans text-foreground/80 focus:outline-none focus:border-foreground/30 transition-colors placeholder:text-foreground/20"
                    placeholder="Mínimo 8 caracteres"
                    minLength={8}
                  />
                </div>
                
                <div className="space-y-2 pt-2">
                  <label className="block text-[10px] uppercase tracking-[0.2em] font-sans text-foreground/50 ml-1">
                    Confirmar Nova Senha
                  </label>
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full bg-transparent border-b border-foreground/10 px-1 py-3 text-sm font-sans text-foreground/80 focus:outline-none focus:border-foreground/30 transition-colors placeholder:text-foreground/20"
                    placeholder="Repita a nova senha"
                    minLength={8}
                  />
                </div>
                
                <div className="pt-6">
                  <Button 
                    type="submit" 
                    variant="outline" 
                    className="w-full text-[10px] uppercase tracking-[0.2em] py-4"
                    disabled={isSubmitting || !newPassword || !confirmPassword}
                  >
                    {isSubmitting ? 'Salvando...' : 'Redefinir senha'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </ProgressiveReveal>

        {!success && (
          <ProgressiveReveal delay={1000}>
            <footer className="pt-12 text-center">
              <Link 
                to="/login" 
                className="text-[10px] font-serif italic text-foreground/30 hover:text-foreground/50 transition-colors uppercase tracking-[0.2em]"
              >
                Cancelar
              </Link>
            </footer>
          </ProgressiveReveal>
        )}

      </div>
    </div>
  );
}
