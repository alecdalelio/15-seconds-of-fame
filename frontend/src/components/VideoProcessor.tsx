import React, { useState } from 'react';
import { PlayIcon } from '@heroicons/react/24/outline';
import { useVideoProcessing } from '../hooks/useVideoProcessing';
import { isValidYouTubeUrl } from '../utils/validation';
import { ProcessingStatus } from './ProcessingStatus';
import { ErrorMessage } from './ErrorMessage';
import { ClipCard } from './ClipCard';
import type { Clip } from '../types/api';

export const VideoProcessor: React.FC = () => {
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
                <ClipCard key={clip.id} clip={clip} index={index} />
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
