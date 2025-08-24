import { useCallback, useRef, useState } from 'react';

interface MediaManager {
  playAudio: (clipId: string, audioUrl: string) => void;
  playVideo: (clipId: string, videoElement: HTMLVideoElement) => void;
  stopAllMedia: () => void;
  getCurrentlyPlaying: () => { type: 'audio' | 'video' | null; clipId: string | null };
  cleanup: () => void;
}

export const useMediaManager = (): MediaManager => {
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const currentVideoRef = useRef<HTMLVideoElement | null>(null);
  const [currentClipId, setCurrentClipId] = useState<string | null>(null);
  const [currentMediaType, setCurrentMediaType] = useState<'audio' | 'video' | null>(null);

  const stopAllMedia = useCallback(() => {
    // Stop current audio
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current.src = '';
      currentAudioRef.current = null;
    }

    // Stop current video
    if (currentVideoRef.current) {
      currentVideoRef.current.pause();
      currentVideoRef.current.currentTime = 0;
      currentVideoRef.current = null;
    }

    setCurrentClipId(null);
    setCurrentMediaType(null);
  }, []);

  const playAudio = useCallback((clipId: string, audioUrl: string) => {
    // If the same clip is already playing, stop it and return
    if (currentClipId === clipId && currentMediaType === 'audio') {
      if (currentAudioRef.current) {
        currentAudioRef.current.pause();
        currentAudioRef.current.currentTime = 0;
        currentAudioRef.current.src = '';
        currentAudioRef.current = null;
      }
      setCurrentClipId(null);
      setCurrentMediaType(null);
      return;
    }

    // Stop any currently playing media
    stopAllMedia();

    // Create new audio element
    const audio = new Audio(audioUrl);
    
    // Add event listeners
    audio.addEventListener('loadstart', () => {
      console.log('Loading audio for clip:', clipId);
    });
    
    audio.addEventListener('canplay', () => {
      console.log('Audio ready to play for clip:', clipId);
      audio.play().catch(error => {
        console.error('Error playing audio:', error);
      });
    });
    
    audio.addEventListener('ended', () => {
      console.log('Audio finished for clip:', clipId);
      if (currentClipId === clipId && currentMediaType === 'audio') {
        currentAudioRef.current = null;
        setCurrentClipId(null);
        setCurrentMediaType(null);
      }
    });
    
    audio.addEventListener('error', (e) => {
      console.error('Error playing audio for clip:', clipId, e);
      if (currentClipId === clipId && currentMediaType === 'audio') {
        currentAudioRef.current = null;
        setCurrentClipId(null);
        setCurrentMediaType(null);
      }
    });
    
    // Set current media
    currentAudioRef.current = audio;
    setCurrentClipId(clipId);
    setCurrentMediaType('audio');
    
    // Load and play
    audio.load();
  }, [stopAllMedia, currentClipId, currentMediaType]);

  const playVideo = useCallback((clipId: string, videoElement: HTMLVideoElement) => {
    // Stop any currently playing media
    stopAllMedia();

    // Set current media
    currentVideoRef.current = videoElement;
    setCurrentClipId(clipId);
    setCurrentMediaType('video');

    // Add event listeners to track when video ends
    const handleEnded = () => {
      if (currentClipId === clipId && currentMediaType === 'video') {
        currentVideoRef.current = null;
        setCurrentClipId(null);
        setCurrentMediaType(null);
      }
    };

    videoElement.addEventListener('ended', handleEnded);
    
    // Play the video
    videoElement.play().catch(error => {
      console.error('Error playing video for clip:', clipId, error);
      if (currentClipId === clipId && currentMediaType === 'video') {
        currentVideoRef.current = null;
        setCurrentClipId(null);
        setCurrentMediaType(null);
      }
    });
  }, [stopAllMedia, currentClipId, currentMediaType]);

  const getCurrentlyPlaying = useCallback(() => {
    return {
      type: currentMediaType,
      clipId: currentClipId
    };
  }, [currentMediaType, currentClipId]);

  const cleanup = useCallback(() => {
    stopAllMedia();
  }, [stopAllMedia]);

  return {
    playAudio,
    playVideo,
    stopAllMedia,
    getCurrentlyPlaying,
    cleanup
  };
};
