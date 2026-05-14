import React from 'react';
import { NavLink } from 'react-router-dom';
import { useScrollDirection } from '../../hooks/useScrollDirection';
import { Home, BookOpen, Feather } from 'lucide-react';

export default function BottomNav() {
  const scrollDir = useScrollDirection();
  
  // O BottomNav se esconde no scroll para baixo, dando mais espaço para a leitura (imersão)
  const isHidden = scrollDir === 'down';

  return (
    <div 
      className={`fixed bottom-0 left-0 right-0 z-50 transition-transform duration-300 ease-out ${
        isHidden ? 'translate-y-full' : 'translate-y-0'
      }`}
    >
      <div className="mx-auto max-w-xl bg-background border-t border-foreground/[0.03] pb-[env(safe-area-inset-bottom)]">
        <nav className="flex justify-around items-center px-4 py-3">
          
          <NavLink 
            to="/" 
            className={({ isActive }) => 
              `flex flex-col items-center space-y-1 transition-opacity duration-300 ${
                isActive ? 'opacity-100' : 'opacity-40 hover:opacity-70'
              }`
            }
          >
            <Home size={20} strokeWidth={1.5} />
            <span className="text-[10px] uppercase tracking-widest">Início</span>
          </NavLink>

          <NavLink 
            to="/bible/explain" 
            className={({ isActive }) => 
              `flex flex-col items-center space-y-1 transition-opacity duration-300 ${
                isActive ? 'opacity-100' : 'opacity-40 hover:opacity-70'
              }`
            }
          >
            <BookOpen size={20} strokeWidth={1.5} />
            <span className="text-[10px] uppercase tracking-widest">Bíblia</span>
          </NavLink>

          <NavLink 
            to="/reflection/today" 
            className={({ isActive }) => 
              `flex flex-col items-center space-y-1 transition-opacity duration-300 ${
                isActive ? 'opacity-100' : 'opacity-40 hover:opacity-70'
              }`
            }
          >
            <Feather size={20} strokeWidth={1.5} />
            <span className="text-[10px] uppercase tracking-widest">Reflexão</span>
          </NavLink>

        </nav>
      </div>
    </div>
  );
}
