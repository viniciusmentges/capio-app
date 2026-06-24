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
  },
  capio_01: { label: "CAPIO 01", src: "/assets/share-backgrounds/capio_01.jpg", variant: "image" },
  capio_02: { label: "CAPIO 02", src: "/assets/share-backgrounds/capio_02.jpg", variant: "image" },
  capio_03: { label: "CAPIO 03", src: "/assets/share-backgrounds/capio_03.jpg", variant: "image" },
  capio_04: { label: "CAPIO 04", src: "/assets/share-backgrounds/capio_04.jpg", variant: "image" },
  capio_05: { label: "CAPIO 05", src: "/assets/share-backgrounds/capio_05.jpg", variant: "image" },
  capio_06: { label: "CAPIO 06", src: "/assets/share-backgrounds/capio_06.jpg", variant: "image" },
  capio_07: { label: "CAPIO 07", src: "/assets/share-backgrounds/capio_07.jpg", variant: "image" },
  capio_08: { label: "CAPIO 08", src: "/assets/share-backgrounds/capio_08.jpg", variant: "image" },
  capio_09: { label: "CAPIO 09", src: "/assets/share-backgrounds/capio_09.jpg", variant: "image" },
  capio_10: { label: "CAPIO 10", src: "/assets/share-backgrounds/capio_10.jpg", variant: "image" },
  capio_11: { label: "CAPIO 11", src: "/assets/share-backgrounds/capio_11.jpg", variant: "image" }
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
