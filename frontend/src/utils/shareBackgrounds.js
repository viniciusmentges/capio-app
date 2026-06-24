export const SHARE_BACKGROUNDS = {
  gradient_light: {
    label: "Fundo padrão claro",
    src: null,
    variant: "light",
  },
  gradient_dark: {
    label: "Fundo padrão escuro",
    src: null,
    variant: "dark",
  }
};

export function getShareBackground(key, dateSeed = new Date()) {
  // Se a chave for explícita e válida, retorna ela
  if (key && key !== 'random' && SHARE_BACKGROUNDS[key]) {
    return SHARE_BACKGROUNDS[key];
  }
  
  // Se for vazio, random ou inválido, sorteia baseado na data
  // Pegamos apenas as opções que são de fato imagens. 
  // No momento, se não houver imagens cadastradas, o fallback seguro é gradient_light.
  const imageKeys = Object.keys(SHARE_BACKGROUNDS).filter(k => SHARE_BACKGROUNDS[k].variant === 'image');
  
  if (imageKeys.length === 0) {
    return SHARE_BACKGROUNDS.gradient_light;
  }

  const epochDays = Math.floor(dateSeed.getTime() / 86400000);
  const selectedKey = imageKeys[epochDays % imageKeys.length];
  
  return SHARE_BACKGROUNDS[selectedKey];
}
