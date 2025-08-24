import { useCallback, useRef } from 'react';

interface MediaManager {
  playAudio: (clipId: string, audioUrl: string) => void;
  playVideo: (clipId: string, videoElement: HTMLVideoElement) => void;
  stopAllMedia: () => void;
  getCurrentlyPlaying: () => { type: 'audio' | 'video' | null; clipId: string | null };
}

export const useMediaManager = (): MediaManager => {
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const currentVideoRef = useRef<HTMLVideoElement | null>(null);
  const currentClipIdRef = useRef<string | null>(null);
  const currentMediaTypeRef = useRef<'audio' | 'video' | null>(null);

  const stopAllMedia = useCallback(() => {
    // Stop current audio
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }

    // Stop current video
    if (currentVideoRef.current) {
      currentVideoRef.current.pause();
      currentVideoRef.current.currentTime = 0;
      currentVideoRef.current = null;
    }

    currentClipIdRef.current = null;
    currentMediaTypeRef.current = null;
  }, []);

  const playAudio = useCallback((clipId: string, audioUrl: string) => {
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
      if (currentClipIdRef.current === clipId && currentMediaTypeRef.current === 'audio') {
        currentAudioRef.current = null;
        currentClipIdRef.current = null;
        currentMediaTypeRef.current = null;
      }
    });
    
    audio.addEventListener('error', (e) => {
      console.error('Error playing audio for clip:', clipId, e);
      if (currentClipIdRef.current === clipId && currentMediaTypeRef.current === 'audio') {
        currentAudioRef.current = null;
        currentClipIdRef.current = null;
        currentMediaTypeRef.current = null;
      }
    });
    
    // Set current media
    currentAudioRef.current = audio;
    currentClipIdRef.current = clipId;
    currentMediaTypeRef.current = 'audio';
    
    // Load and play
    audio.load();
  }, [stopAllMedia]);

  const playVideo = useCallback((clipId: string, videoElement: HTMLVideoElement) => {
    // Stop any currently playing media
    stopAllMedia();

    // Set current media
    currentVideoRef.current = videoElement;
    currentClipIdRef.current = clipId;
    currentMediaTypeRef.current = 'video';

    // Add event listeners to track when video ends
    const handleEnded = () => {
      if (currentClipIdRef.current === clipId && currentMediaTypeRef.current === 'video') {
        currentVideoRef.current = null;
        currentClipIdRef.current = null;
        currentMediaTypeRef.current = null;
      }
    };

    videoElement.addEventListener('ended', handleEnded);
    
    // Play the video
    videoElement.play().catch(error => {
      console.error('Error playing video for clip:', clipId, error);
      if (currentClipIdRef.current === clipId && currentMediaTypeRef.current === 'video') {
        currentVideoRef.current = null;
        currentClipIdRef.current = null;
        currentMediaTypeRef.current = null;
      }
    });
  }, [stopAllMedia]);

  const getCurrentlyPlaying = useCallback(() => {
    return {
      type: currentMediaTypeRef.current,
      clipId: currentClipIdRef.current
    };
  }, []);

  return {
    playAudio,
    playVideo,
    stopAllMedia,
    getCurrentlyPlaying
  };
};
