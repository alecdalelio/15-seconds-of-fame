import type { Clip } from '../types/api';

const STORAGE_KEY = 'savedClips';

export const loadSavedClips = (): Clip[] => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch (error) {
    console.error('Error loading saved clips from localStorage:', error);
    return [];
  }
};

export const saveClipsToStorage = (clips: Clip[]): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(clips));
  } catch (error) {
    console.error('Error saving clips to localStorage:', error);
  }
};

export const addClipToStorage = (clip: Clip): Clip[] => {
  try {
    const existingClips = loadSavedClips();
    const newClips = [...existingClips, clip];
    saveClipsToStorage(newClips);
    return newClips;
  } catch (error) {
    console.error('Error adding clip to storage:', error);
    return loadSavedClips();
  }
};

export const removeClipFromStorage = (clipId: string): Clip[] => {
  try {
    const existingClips = loadSavedClips();
    const newClips = existingClips.filter(clip => clip.id !== clipId);
    saveClipsToStorage(newClips);
    return newClips;
  } catch (error) {
    console.error('Error removing clip from storage:', error);
    return loadSavedClips();
  }
};

export const clearAllClips = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
    console.log('All clips cleared from storage');
  } catch (error) {
    console.error('Error clearing clips from storage:', error);
  }
};

export const getStorageInfo = (): { count: number; clips: Clip[] } => {
  try {
    const clips = loadSavedClips();
    return {
      count: clips.length,
      clips: clips
    };
  } catch (error) {
    console.error('Error getting storage info:', error);
    return { count: 0, clips: [] };
  }
};
