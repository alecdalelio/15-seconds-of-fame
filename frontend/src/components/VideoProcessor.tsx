import React, { useState } from 'react';
import { PlayIcon, XMarkIcon, VideoCameraIcon, ArrowRightIcon } from '@heroicons/react/24/outline';
import Logo from './Logo';
import { useVideoProcessing } from '../hooks/useVideoProcessing';
import { isValidYouTubeUrl } from '../utils/validation';
import { ProcessingStatus } from './ProcessingStatus';
import { ErrorMessage } from './ErrorMessage';
import { ClipCard } from './ClipCard';
import type { Clip } from '../types/api';

interface VideoProcessorProps {
  savedClips: Clip[];
  currentVideoUrl: string;
  currentVideoResults: Clip[];
  currentVideoTitle: string;
  onVideoProcessed: (url: string, results: Clip[], title: string) => void;
  onClearResults: () => void;
  onSaveClip: (clip: Clip) => void;
  onRemoveClip: (clipId: string) => void;
}

export const VideoProcessor: React.FC<VideoProcessorProps> = ({ 
  savedClips, 
  currentVideoUrl,
  currentVideoResults,
  currentVideoTitle,
  onVideoProcessed,
  onClearResults,
  onSaveClip, 
  onRemoveClip 
}) => {
  const [youtubeUrl, setYoutubeUrl] = useState(currentVideoUrl);
  const [urlError, setUrlError] = useState('');
  const videoProcessing = useVideoProcessing();

  // Update local state when persistent state changes
  React.useEffect(() => {
    setYoutubeUrl(currentVideoUrl);
  }, [currentVideoUrl]);

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

  // Update persistent state when processing succeeds
  React.useEffect(() => {
    if (videoProcessing.isSuccess && videoProcessing.data?.clips) {
      const videoTitle = videoProcessing.data.clips[0]?.video_title || 'Unknown Video';
      onVideoProcessed(youtubeUrl, videoProcessing.data.clips, videoTitle);
    }
  }, [videoProcessing.isSuccess, videoProcessing.data, youtubeUrl, onVideoProcessed]);

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
      
      onSaveClip(clipWithMetadata);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center space-x-3 mb-6">
          <Logo size={64} variant="light" gap={false} />
          <div className="text-left">
            <h1 className="text-3xl sm:text-4xl font-bold gradient-text">
              Create Viral Clips
            </h1>
            <p className="text-lg text-gray-600">
              Transform any YouTube video into viral 15-second clips
            </p>
          </div>
        </div>
        
        <div className="max-w-2xl mx-auto">
          <p className="text-gray-600 leading-relaxed">
            Our AI analyzes your video content and identifies the most engaging moments, 
            creating optimized clips designed to go viral on social media platforms.
          </p>
        </div>
      </div>

      {/* URL Input Section */}
      <div className="max-w-3xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <div className="flex items-center space-x-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  placeholder="Paste a YouTube URL here..."
                  className={`input-field pr-12 ${urlError ? 'border-red-300 focus:ring-red-500' : ''}`}
                  disabled={videoProcessing.isPending}
                />
                <VideoCameraIcon className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
              <button
                type="submit"
                disabled={videoProcessing.isPending}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {videoProcessing.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <PlayIcon className="w-5 h-5" />
                    <span>Process Video</span>
                  </>
                )}
              </button>
            </div>
            {urlError && (
              <p className="text-red-600 text-sm mt-2 flex items-center space-x-1">
                <XMarkIcon className="w-4 h-4" />
                <span>{urlError}</span>
              </p>
            )}
          </div>
        </form>
      </div>

      {/* Processing Status */}
      {videoProcessing.isPending && (
        <div className="max-w-2xl mx-auto">
          <ProcessingStatus isProcessing={true} />
        </div>
      )}

      {/* Error Display */}
      {videoProcessing.isError && (
        <div className="max-w-2xl mx-auto">
          <ErrorMessage 
            message={videoProcessing.error?.message || 'An error occurred while processing the video.'}
            onRetry={handleRetry}
          />
        </div>
      )}

      {/* Results Section */}
      {currentVideoResults.length > 0 && (
        <div className="space-y-6">
          {/* Results Header */}
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-3">
                <Logo size={24} variant="light" gap={false} />
                <span>Your Viral Clips</span>
                <span className="text-lg text-gray-500">({currentVideoResults.length} clips)</span>
              </h2>
              {currentVideoTitle && (
                <p className="text-gray-600 flex items-center space-x-2">
                  <span>From:</span>
                  <span className="font-medium text-gray-900">{currentVideoTitle}</span>
                </p>
              )}
            </div>
            <div className="flex items-center space-x-3">
              <div className="text-sm text-gray-500">
                Sorted by viral potential
              </div>
              <button
                onClick={onClearResults}
                className="btn-outline flex items-center space-x-2"
              >
                <XMarkIcon className="w-4 h-4" />
                <span>Clear Results</span>
              </button>
            </div>
          </div>

          {/* Clips Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {currentVideoResults.map((clip, index) => (
              <ClipCard
                key={clip.id}
                clip={clip}
                index={index}
                onSaveToLibrary={(clip) => handleSaveToLibrary(clip, index)}
                isSaved={savedClips.some(savedClip => savedClip.id === clip.id)}
              />
            ))}
          </div>

          {/* Call to Action */}
          <div className="text-center py-8">
            <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-2xl p-8 border border-primary-200/50">
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Ready to create more viral content?
              </h3>
              <p className="text-gray-600 mb-4">
                Try processing another video or explore your saved clips library.
              </p>
              <div className="flex items-center justify-center space-x-4">
                <button
                  onClick={() => setYoutubeUrl('')}
                  className="btn-primary"
                >
                  Process Another Video
                </button>
                <div className="flex items-center space-x-2 text-gray-500">
                  <span>or</span>
                  <ArrowRightIcon className="w-4 h-4" />
                  <span>Check your library</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
