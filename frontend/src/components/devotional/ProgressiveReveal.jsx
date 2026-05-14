import React, { useState, useEffect } from 'react';

export default function ProgressiveReveal({ delay = 0, duration = 900, children }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(true);
    }, delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div 
      className={`transition-all ease-out ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-1'
      }`}
      style={{ transitionDuration: `${duration}ms` }}
    >
      {children}
    </div>
  );
}
