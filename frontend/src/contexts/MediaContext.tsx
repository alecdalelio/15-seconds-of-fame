import React, { createContext, useContext } from 'react';
import { useMediaManager } from '../hooks/useMediaManager';

interface MediaContextType {
  playAudio: (clipId: string, audioUrl: string) => void;
  playVideo: (clipId: string, videoElement: HTMLVideoElement) => void;
  stopAllMedia: () => void;
  getCurrentlyPlaying: () => { type: 'audio' | 'video' | null; clipId: string | null };
  cleanup: () => void;
}

const MediaContext = createContext<MediaContextType | null>(null);

export const MediaProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const mediaManager = useMediaManager();

  return (
    <MediaContext.Provider value={mediaManager}>
      {children}
    </MediaContext.Provider>
  );
};

export const useMediaContext = (): MediaContextType => {
  const context = useContext(MediaContext);
  if (!context) {
    throw new Error('useMediaContext must be used within a MediaProvider');
  }
  return context;
};
