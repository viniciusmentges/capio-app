import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Card from '../../components/ui/Card';
import Input from '../../components/ui/Input';
import Button from '../../components/ui/Button';
import ErrorState from '../../components/ui/ErrorState';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    setError('');

    try {
      await login({ username: email, password });
      navigate('/');
    } catch (err) {
      setError('Não foi possível entrar. Verifique seus dados e tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col justify-center min-h-screen px-6 py-12 max-w-sm mx-auto space-y-20 animate-fade-in">
      <div className="space-y-4 text-center">
        <h1 className="font-serif text-3xl text-foreground tracking-tight">CAPIO</h1>
        <p className="text-[10px] uppercase tracking-[0.3em] text-foreground/40 font-sans">
          Espaço de Presença
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-12">
        <div className="space-y-6">
          <Input 
            type="email" 
            placeholder="Seu email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
            className="bg-transparent border-b border-foreground/10 rounded-none px-0 py-4 focus:border-foreground/30 transition-colors"
          />
          <Input 
            type="password" 
            placeholder="Sua senha" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
            className="bg-transparent border-b border-foreground/10 rounded-none px-0 py-4 focus:border-foreground/30 transition-colors"
          />
        </div>

        {error && (
          <div className="py-2">
            <p className="text-xs text-foreground/50 text-center font-serif italic">{error}</p>
          </div>
        )}

        <Button 
          type="submit" 
          className="w-full py-4 text-xs uppercase tracking-[0.2em] opacity-80 hover:opacity-100" 
          disabled={loading}
        >
          {loading ? 'Entrando...' : 'Entrar'}
        </Button>
      </form>

      <div className="flex flex-col items-center space-y-6">
        <Link 
          to="/register" 
          className="text-[10px] uppercase tracking-[0.2em] text-foreground/30 hover:text-foreground/50 transition-colors"
        >
          Criar conta
        </Link>
        
        <Link 
          to="/recuperar-senha" 
          className="text-[10px] uppercase tracking-[0.2em] text-foreground/15 hover:text-foreground/30 transition-colors"
        >
          Esqueci minha senha
        </Link>
      </div>

    </div>
  );
}
