export const DEVOTIONAL_SHARE_BACKGROUNDS = [
  'capio_devotional_01',
  'capio_devotional_02',
  'capio_devotional_03'
];

export function getShareDevotionalBackground(bgImageId) {
  if (bgImageId && bgImageId !== 'random' && DEVOTIONAL_SHARE_BACKGROUNDS.includes(bgImageId)) {
    return `/assets/share-backgrounds-devotional/${bgImageId}.jpg`;
  }
  
  // Random selection
  const randomIndex = Math.floor(Math.random() * DEVOTIONAL_SHARE_BACKGROUNDS.length);
  const randomBg = DEVOTIONAL_SHARE_BACKGROUNDS[randomIndex];
  
  return `/assets/share-backgrounds-devotional/${randomBg}.jpg`;
}
