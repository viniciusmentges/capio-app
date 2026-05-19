import React, { createContext, useContext, useState, useEffect } from 'react';

const TextSizeContext = createContext();

export function TextSizeProvider({ children }) {
  const [textSize, setTextSize] = useState(() => {
    return localStorage.getItem('capio_text_size') || 'base';
  });

  useEffect(() => {
    localStorage.setItem('capio_text_size', textSize);
  }, [textSize]);

  return (
    <TextSizeContext.Provider value={{ textSize, setTextSize }}>
      <div className={`capio-text-${textSize} w-full h-full flex flex-col flex-1`}>
        {children}
      </div>
    </TextSizeContext.Provider>
  );
}

export function useTextSize() {
  const context = useContext(TextSizeContext);
  if (!context) {
    throw new Error('useTextSize must be used within a TextSizeProvider');
  }
  return context;
}
