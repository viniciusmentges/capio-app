import { useState, useEffect } from 'react';

export function useScrollDirection() {
  const [scrollDir, setScrollDir] = useState('up');

  useEffect(() => {
    let lastY = window.scrollY;
    const threshold = 10;

    const updateDir = () => {
      const y = window.scrollY;

      if (Math.abs(y - lastY) < threshold) return;

      setScrollDir(y > lastY ? 'down' : 'up');
      lastY = y;
    };

    window.addEventListener('scroll', updateDir);

    return () => window.removeEventListener('scroll', updateDir);
  }, []);

  return scrollDir;
}
