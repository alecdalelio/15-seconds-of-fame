import React, { useState } from 'react';
import { PlayIcon } from '@heroicons/react/24/outline';
import { useVideoProcessing } from '../hooks/useVideoProcessing';
import { isValidYouTubeUrl } from '../utils/validation';
import { ProcessingStatus } from './ProcessingStatus';
import { ErrorMessage } from './ErrorMessage';
import { ClipCard } from './ClipCard';
import type { Clip } from '../types/api';

interface VideoProcessorProps {
  savedClips: Clip[];
  onSaveClip: (clip: Clip) => void;
  onRemoveClip: (clipId: string) => void;
}

export const VideoProcessor: React.FC<VideoProcessorProps> = ({ 
  savedClips, 
  onSaveClip, 
  onRemoveClip 
}) => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [urlError, setUrlError] = useState('');
  const videoProcessing = useVideoProcessing();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate URL
    if (!youtubeUrl.trim()) {
      setUrlError('Please enter a YouTube URL');
      return;
    }
    
    if (!isValidYouTubeUrl(youtubeUrl)) {
      setUrlError('Please enter a valid YouTube URL');
      return;
    }
    
    setUrlError('');
    
    // Process video
    videoProcessing.mutate({ youtube_url: youtubeUrl.trim() });
  };

  const handleRetry = () => {
    if (youtubeUrl.trim() && isValidYouTubeUrl(youtubeUrl)) {
      videoProcessing.mutate({ youtube_url: youtubeUrl.trim() });
    }
  };

  const handleSaveToLibrary = (clip: Clip, index: number) => {
    // Check if clip is already saved
    const isAlreadySaved = savedClips.some(savedClip => savedClip.id === clip.id);
    
    if (isAlreadySaved) {
      // Remove from saved clips
      onRemoveClip(clip.id);
    } else {
      // Add to saved clips with enhanced metadata
      const clipWithMetadata = {
        ...clip,
        ai_generated: true,
        title: clip.title || `Viral Clip ${index + 1}`,
        duration: `${Math.round(clip.end_time - clip.start_time)}s`,
        // Use video information from the API response
        video_source: clip.video_source || youtubeUrl,
        video_title: clip.video_title || 'Unknown Video',
        // Preserve all viral analysis data
        viral_score: clip.viral_score,
        emotional_intensity: clip.emotional_intensity,
        controversy_level: clip.controversy_level,
        relatability: clip.relatability,
        educational_value: clip.educational_value,
        entertainment_factor: clip.entertainment_factor,
        combined_score: clip.combined_score,
        suggested_caption: clip.suggested_caption
      };
      
      // Debug logging
      console.log('Saving clip with video title:', clipWithMetadata.video_title);
      console.log('Full clip metadata:', clipWithMetadata);
      onSaveClip(clipWithMetadata);
    }
  };

  const isClipSaved = (clipId: string) => {
    return savedClips.some(savedClip => savedClip.id === clipId);
  };

  const isProcessing = videoProcessing.isPending;
  const hasError = videoProcessing.isError;
  const hasResults = videoProcessing.isSuccess && videoProcessing.data?.clips;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          15 Seconds of Fame
        </h1>
        <p className="text-gray-600">
          Transform any YouTube video into viral 15-second clips with AI-powered scoring
        </p>
      </div>

      {/* Main Content */}
      <div className="space-y-6">
        {/* Input Form */}
        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 mb-2">
                YouTube Video URL
              </label>
              <div className="flex gap-3">
                <input
                  id="youtube-url"
                  type="url"
                  value={youtubeUrl}
                  onChange={(e) => {
                    setYoutubeUrl(e.target.value);
                    if (urlError) setUrlError('');
                  }}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="input-field flex-1"
                  disabled={isProcessing}
                />
                <button
                  type="submit"
                  disabled={isProcessing}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {isProcessing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-4 w-4" />
                      Process Video
                    </>
                  )}
                </button>
              </div>
              {urlError && (
                <p className="mt-1 text-sm text-red-600">{urlError}</p>
              )}
            </div>
          </form>
        </div>

        {/* Processing Status */}
        {isProcessing && <ProcessingStatus isProcessing={isProcessing} />}

        {/* Error Display */}
        {hasError && (
          <ErrorMessage 
            message={videoProcessing.error?.message || 'An error occurred while processing the video.'}
            onRetry={handleRetry}
          />
        )}

        {/* Results Display */}
        {hasResults && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                Your Viral Clips ({videoProcessing.data.clips.length} clips)
              </h2>
              <div className="text-sm text-gray-500">
                Sorted by viral potential
              </div>
            </div>
            
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {videoProcessing.data.clips.map((clip: Clip, index: number) => (
                <ClipCard 
                  key={clip.id} 
                  clip={clip} 
                  index={index}
                  onSaveToLibrary={(clipToSave) => handleSaveToLibrary(clipToSave, index)}
                  isSaved={isClipSaved(clip.id)}
                />
              ))}
            </div>
            
            <div className="text-center text-sm text-gray-500 mt-6">
              <p>💡 Tip: Higher scores indicate better viral potential!</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
