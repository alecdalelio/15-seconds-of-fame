import React, { useState, useRef } from 'react';
import { PlayIcon, StopIcon, ClockIcon, ChevronDownIcon, ChevronUpIcon, HeartIcon, VideoCameraIcon, ArrowDownTrayIcon, SparklesIcon, FireIcon } from '@heroicons/react/24/outline';
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
    <div className="bg-white rounded-2xl shadow-soft hover:shadow-medium transition-all duration-300 border border-gray-100/50 overflow-hidden group animate-slide-up">
      {/* Header with Gradient Background */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50 p-6 border-b border-gray-100/50">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center shadow-glow">
                <span className="text-white font-bold text-lg">#{index + 1}</span>
              </div>
              {clip.score >= 6.0 && (
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-accent-500 rounded-full flex items-center justify-center">
                  <FireIcon className="w-2.5 h-2.5 text-white" />
                </div>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-bold text-gray-900 text-lg leading-tight mb-1">
                {clip.title || `Clip ${index + 1}`}
              </h3>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="flex items-center space-x-1 bg-white/70 px-2 py-1 rounded-lg">
                  <ClockIcon className="h-4 w-4 text-primary-500" />
                  <span className="font-medium">{formatTime(clip.start_time)} - {formatTime(clip.end_time)}</span>
                </div>
                <div className="bg-accent-100 text-accent-700 px-2 py-1 rounded-lg text-xs font-semibold">
                  {formatTime(clip.end_time - clip.start_time)}
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col items-end space-y-2">
            <ScoreDisplay score={clip.score} size="lg" showLabel={false} />
            <div className="flex items-center space-x-1 bg-white/70 px-2 py-1 rounded-lg">
              <SparklesIcon className="h-3 w-3 text-secondary-500" />
              <span className="text-xs font-medium text-gray-600">AI Generated</span>
            </div>
          </div>
        </div>
      </div>

      {/* Video Player Section */}
      {clip.video_clip_path && (
        <div className="p-6 border-b border-gray-100/50">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-sm font-semibold text-gray-700 flex items-center space-x-2">
              <VideoCameraIcon className="h-4 w-4 text-primary-500" />
              <span>Video Preview</span>
            </h4>
            <button
              onClick={() => setShowVideo(!showVideo)}
              className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700 transition-colors px-3 py-1.5 rounded-lg hover:bg-primary-50 font-medium"
            >
              <span>{showVideo ? 'Hide' : 'Show'} Video</span>
            </button>
          </div>
          
          {showVideo && (
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-200/50">
              <video 
                ref={videoRef}
                controls 
                className="w-full rounded-lg shadow-soft"
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

      {/* Content Section */}
      <div className="p-6 space-y-4">
        {/* Transcript */}
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center space-x-2">
            <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
            <span>Transcript</span>
          </h4>
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200/50">
            <p className="text-sm text-gray-700 leading-relaxed">
              {clip.transcript ? truncateText(clip.transcript, 200) : 'No transcript available'}
            </p>
          </div>
        </div>

        {/* Suggested Caption */}
        {clip.suggested_caption && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center space-x-2">
              <span className="w-2 h-2 bg-secondary-500 rounded-full"></span>
              <span>Suggested Caption</span>
            </h4>
            <div className="bg-gradient-to-r from-secondary-50 to-primary-50 rounded-xl p-4 border border-secondary-200/50">
              <p className="text-sm text-gray-700 leading-relaxed font-medium">
                {clip.suggested_caption}
              </p>
            </div>
          </div>
        )}

        {/* Viral Analysis Toggle */}
        {(clip.viral_score || clip.combined_score) && (
          <div>
            <button
              onClick={() => setShowViralAnalysis(!showViralAnalysis)}
              className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700 transition-colors px-3 py-2 rounded-lg hover:bg-primary-50 font-medium w-full justify-center"
            >
              {showViralAnalysis ? (
                <ChevronUpIcon className="h-4 w-4" />
              ) : (
                <ChevronDownIcon className="h-4 w-4" />
              )}
              <span>{showViralAnalysis ? 'Hide' : 'Show'} AI Viral Analysis</span>
            </button>
            
            {showViralAnalysis && (
              <div className="mt-4 pt-4 border-t border-gray-100">
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
      </div>

      {/* Action Buttons */}
      <div className="p-6 bg-gray-50/50 border-t border-gray-100/50">
        <div className="flex flex-wrap items-center justify-between gap-3">
          {/* Primary Actions */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handlePlayAudio}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                isThisClipPlaying && currentlyPlaying.type === 'audio'
                  ? 'bg-success-100 text-success-700 shadow-soft'
                  : 'bg-primary-100 text-primary-700 hover:bg-primary-200 shadow-soft'
              }`}
            >
              {isThisClipPlaying && currentlyPlaying.type === 'audio' ? (
                <StopIcon className="h-4 w-4" />
              ) : (
                <PlayIcon className="h-4 w-4" />
              )}
              <span>{isThisClipPlaying && currentlyPlaying.type === 'audio' ? 'Stop' : 'Play'} Audio</span>
            </button>
            
            {onSaveToLibrary && (
              <button
                onClick={() => onSaveToLibrary(clip)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isSaved 
                    ? 'bg-secondary-100 text-secondary-700 shadow-soft' 
                    : 'bg-gray-100 text-gray-700 hover:bg-secondary-100 hover:text-secondary-700 shadow-soft'
                }`}
              >
                <HeartIcon className={`h-4 w-4 ${isSaved ? 'fill-current' : ''}`} />
                <span>{isSaved ? 'Saved' : 'Save'}</span>
              </button>
            )}
          </div>

          {/* Download Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadAudio}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm text-gray-600 hover:text-primary-600 transition-colors hover:bg-primary-50"
            >
              <ArrowDownTrayIcon className="h-4 w-4" />
              <span className="hidden sm:inline">Audio</span>
            </button>
            
            {clip.video_clip_path && (
              <button
                onClick={handleDownloadVideo}
                className="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm text-gray-600 hover:text-primary-600 transition-colors hover:bg-primary-50"
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
                <span className="hidden sm:inline">Video</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
