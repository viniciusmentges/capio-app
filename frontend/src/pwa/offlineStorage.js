import localforage from 'localforage';
import { OFFLINE_KEYS } from './offlineKeys';

// Configuração premium do localForage voltada aoIndexedDB
localforage.config({
  name: 'capio_pwa_db',
  storeName: 'capio_offline_store',
  description: 'Persistência local e silenciosa da CAPIO para suporte offline e resiliência de alto nível',
});

/**
 * Auxiliar para comparar e encontrar o índice de um item duplicado na lista
 */
function findDuplicateIndex(list, newItem) {
  if (!Array.isArray(list)) return -1;
  
  // 1. Tentar correspondência direta por ID (se disponível)
  if (newItem.id !== undefined && newItem.id !== null) {
    return list.findIndex(item => item.id === newItem.id);
  }
  
  // 2. Tentar por referência bíblica ou passagem digitada (para explicações bíblicas)
  const newRef = newItem.reference_display || newItem.passage;
  if (newRef) {
    return list.findIndex(item => {
      const itemRef = item.reference_display || item.passage;
      return itemRef && itemRef.toLowerCase() === newRef.toLowerCase();
    });
  }
  
  // 3. Fallback de comparação profunda sutil para objetos
  return list.findIndex(item => JSON.stringify(item) === JSON.stringify(newItem));
}

/**
 * Salva um novo item em uma lista offline versionada (limite automático de 3 itens)
 * Se o item já existir, reposiciona para o topo (como o mais recente)
 * Nunca persiste dados sensíveis como JWT, refresh token ou credenciais
 */
export async function saveOfflineItem(key, newItem, limit = 3) {
  if (!newItem) return;

  try {
    const list = (await localforage.getItem(key)) || [];
    
    // Identificar e remover duplicado se já existir na lista
    const duplicateIndex = findDuplicateIndex(list, newItem);
    if (duplicateIndex !== -1) {
      list.splice(duplicateIndex, 1);
    }
    
    // Preponderar o novo item (topo da fila, mais recente)
    list.unshift(newItem);
    
    // Cortar para manter apenas o limite definido (padrão 3)
    const limitedList = list.slice(0, limit);
    
    await localforage.setItem(key, limitedList);
  } catch (error) {
    console.error(`[Storage Offline] Erro ao salvar chave ${key}:`, error);
  }
}

/**
 * Recupera todos os itens salvos sob uma determinada chave
 */
export async function getOfflineItems(key) {
  try {
    const list = await localforage.getItem(key);
    return Array.isArray(list) ? list : [];
  } catch (error) {
    console.error(`[Storage Offline] Erro ao ler chave ${key}:`, error);
    return [];
  }
}

/**
 * Recupera o item offline mais recente (primeiro da lista)
 */
export async function getLatestOfflineItem(key) {
  try {
    const list = await getOfflineItems(key);
    return list.length > 0 ? list[0] : null;
  } catch (error) {
    console.error(`[Storage Offline] Erro ao obter mais recente da chave ${key}:`, error);
    return null;
  }
}

/**
 * Salva as preferências básicas do usuário
 */
export async function saveUserPreferences(prefs) {
  try {
    const current = (await localforage.getItem(OFFLINE_KEYS.USER_PREFERENCES)) || {};
    const updated = { ...current, ...prefs };
    await localforage.setItem(OFFLINE_KEYS.USER_PREFERENCES, updated);
  } catch (error) {
    console.error('[Storage Offline] Erro ao salvar preferências do usuário:', error);
  }
}

/**
 * Recupera as preferências básicas do usuário
 */
export async function getUserPreferences() {
  try {
    return (await localforage.getItem(OFFLINE_KEYS.USER_PREFERENCES)) || {};
  } catch (error) {
    console.error('[Storage Offline] Erro ao ler preferências do usuário:', error);
    return {};
  }
}
