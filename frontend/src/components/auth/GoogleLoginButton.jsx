import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';

export default function GoogleLoginButton({ onSuccess, onError, text = "continue_with" }) {
  const [loading, setLoading] = useState(false);

  return (
    <div className="w-full flex justify-center opacity-90 hover:opacity-100 transition-opacity">
      <div className="w-full relative" style={{ height: '44px' }}>
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10 text-[10px] uppercase tracking-[0.2em] text-foreground/50">
            Aguarde...
          </div>
        )}
        <GoogleLogin
          onSuccess={(credentialResponse) => {
            setLoading(true);
            onSuccess(credentialResponse.credential).finally(() => {
              setLoading(false);
            });
          }}
          onError={() => {
            if (onError) onError();
          }}
          useOneTap
          theme="outline"
          size="large"
          text={text}
          shape="square"
          width="100%"
        />
      </div>
    </div>
  );
}
