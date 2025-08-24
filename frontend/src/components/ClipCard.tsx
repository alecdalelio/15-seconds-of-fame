import React, { useState, useRef } from 'react';
import { PlayIcon, ClockIcon, ChevronDownIcon, ChevronUpIcon, HeartIcon, VideoCameraIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import type { Clip } from '../types/api';
import { ScoreDisplay } from './ScoreDisplay';
import { ViralAnalysisDisplay } from './ViralAnalysisDisplay';
import { useMediaContext } from '../contexts/MediaContext';
import { formatTime, truncateText } from '../utils/validation';

interface ClipCardProps {
  clip: Clip;
  index: number;
  onSaveToLibrary?: (clip: Clip) => void;
  isSaved?: boolean;
}

export const ClipCard: React.FC<ClipCardProps> = ({ clip, index, onSaveToLibrary, isSaved = false }) => {
  const [showViralAnalysis, setShowViralAnalysis] = useState(false);
  const [showVideo, setShowVideo] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const { playAudio, playVideo, getCurrentlyPlaying } = useMediaContext();

  const handlePlayAudio = () => {
    const audioUrl = `http://localhost:8000/audio/${clip.id}`;
    playAudio(clip.id, audioUrl);
  };

  const handleVideoPlay = () => {
    if (videoRef.current) {
      playVideo(clip.id, videoRef.current);
    }
  };

  const handleDownloadAudio = () => {
    const link = document.createElement('a');
    link.href = `http://localhost:8000/audio/${clip.id}`;
    link.download = `clip_${clip.id}.mp3`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadVideo = () => {
    if (clip.video_clip_path) {
      const link = document.createElement('a');
      link.href = `http://localhost:8000/video/${clip.id}`;
      link.download = `clip_${clip.id}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // Check if this clip is currently playing
  const currentlyPlaying = getCurrentlyPlaying();
  const isThisClipPlaying = currentlyPlaying.clipId === clip.id;

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      {/* Header - Responsive Layout */}
      <div className="text-center mb-3">
        <div className="flex justify-center mb-1">
          <div className="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
            #{index + 1}
          </div>
        </div>
        
        <div className="text-center mb-2">
          <h3 className="font-semibold text-gray-900 text-sm sm:text-base break-words">
            {clip.title || `Clip ${index + 1}`}
          </h3>
        </div>
        
        <div className="flex items-center justify-center gap-3 mb-2">
          <div className="flex items-center gap-1.5 text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full min-w-0 flex-shrink-0">
            <ClockIcon className="h-3 w-3 flex-shrink-0" />
            <span className="font-medium whitespace-nowrap">{formatTime(clip.start_time)} - {formatTime(clip.end_time)}</span>
          </div>
          <div className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-full flex-shrink-0">
            <span className="font-medium">{formatTime(clip.end_time - clip.start_time)}</span>
          </div>
        </div>
        
        <div className="flex justify-center">
          <ScoreDisplay score={clip.score} size="sm" showLabel={false} />
        </div>
      </div>

      {/* Video Player Section */}
      {clip.video_clip_path && (
        <div className="mb-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
            <h4 className="text-sm font-medium text-gray-700">Video Clip</h4>
            <button
              onClick={() => setShowVideo(!showVideo)}
              className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-primary-600 hover:text-primary-700 transition-colors px-2 py-1.5 rounded-md hover:bg-primary-50 self-start sm:self-auto"
            >
              <VideoCameraIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              <span>{showVideo ? 'Hide' : 'Show'} Video</span>
            </button>
          </div>
          
          {showVideo && (
            <div className="bg-gray-100 rounded-lg p-2 sm:p-4">
              <video 
                ref={videoRef}
                controls 
                className="w-full rounded-lg"
                src={`http://localhost:8000/video/${clip.id}`}
                preload="metadata"
                onPlay={handleVideoPlay}
              >
                Your browser does not support the video tag.
              </video>
            </div>
          )}
        </div>
      )}

      <div className="space-y-3">
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-1">Transcript</h4>
          <p className="text-xs sm:text-sm text-gray-600 bg-gray-50 rounded-lg p-2 sm:p-3">
            {clip.transcript ? truncateText(clip.transcript, 150) : 'No transcript available'}
          </p>
        </div>

        {clip.suggested_caption && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-1">Suggested Caption</h4>
            <p className="text-xs sm:text-sm text-gray-600 bg-blue-50 rounded-lg p-2 sm:p-3 border border-blue-200">
              {clip.suggested_caption}
            </p>
          </div>
        )}

        {/* Viral Analysis Toggle */}
        {(clip.viral_score || clip.combined_score) && (
          <div>
            <button
              onClick={() => setShowViralAnalysis(!showViralAnalysis)}
              className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-primary-600 hover:text-primary-700 transition-colors px-2 py-1.5 rounded-md hover:bg-primary-50"
            >
              {showViralAnalysis ? (
                <ChevronUpIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              ) : (
                <ChevronDownIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              )}
              <span>{showViralAnalysis ? 'Hide' : 'Show'} AI Viral Analysis</span>
            </button>
            
            {showViralAnalysis && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <ViralAnalysisDisplay
                  viral_score={clip.viral_score}
                  emotional_intensity={clip.emotional_intensity}
                  controversy_level={clip.controversy_level}
                  relatability={clip.relatability}
                  educational_value={clip.educational_value}
                  entertainment_factor={clip.entertainment_factor}
                  combined_score={clip.combined_score}
                  viral_reasoning={clip.reasoning}
                />
              </div>
            )}
          </div>
        )}

        <div className="pt-3 border-t border-gray-100">
          {/* Action Buttons - Responsive Layout */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            {/* Button Group - Stacks vertically on mobile, horizontal on larger screens */}
            <div className="flex flex-wrap items-center gap-2 sm:gap-3">
              <button
                onClick={handlePlayAudio}
                className={`flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm transition-colors px-2 py-1.5 rounded-md ${
                  isThisClipPlaying && currentlyPlaying.type === 'audio'
                    ? 'text-green-600 bg-green-50 hover:bg-green-100'
                    : 'text-primary-600 hover:text-primary-700 hover:bg-primary-50'
                }`}
              >
                <PlayIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">
                  {isThisClipPlaying && currentlyPlaying.type === 'audio' ? 'Playing Audio' : 'Play Audio'}
                </span>
                <span className="sm:hidden">
                  {isThisClipPlaying && currentlyPlaying.type === 'audio' ? 'Playing' : 'Audio'}
                </span>
              </button>
              
              <button
                onClick={handleDownloadAudio}
                className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-gray-600 hover:text-primary-600 transition-colors px-2 py-1.5 rounded-md hover:bg-gray-50"
              >
                <ArrowDownTrayIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Download Audio</span>
                <span className="sm:hidden">Audio</span>
              </button>
              
              {clip.video_clip_path && (
                <button
                  onClick={handleDownloadVideo}
                  className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-gray-600 hover:text-primary-600 transition-colors px-2 py-1.5 rounded-md hover:bg-gray-50"
                >
                  <ArrowDownTrayIcon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
                  <span className="hidden sm:inline">Download Video</span>
                  <span className="sm:hidden">Video</span>
                </button>
              )}
              
              {onSaveToLibrary && (
                <button
                  onClick={() => onSaveToLibrary(clip)}
                  className={`flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm transition-colors px-2 py-1.5 rounded-md ${
                    isSaved 
                      ? 'text-red-600 hover:text-red-700 hover:bg-red-50' 
                      : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                  }`}
                >
                  <HeartIcon className={`h-3.5 w-3.5 sm:h-4 sm:w-4 ${isSaved ? 'fill-current' : ''}`} />
                  <span className="hidden sm:inline">{isSaved ? 'Saved' : 'Save to Library'}</span>
                  <span className="sm:hidden">{isSaved ? 'Saved' : 'Save'}</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
