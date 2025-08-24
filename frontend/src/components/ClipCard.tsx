import React from 'react';
import { PlayIcon, ClockIcon } from '@heroicons/react/24/outline';
import type { Clip } from '../types/api';
import { ScoreDisplay } from './ScoreDisplay';
import { formatTime, truncateText } from '../utils/validation';

interface ClipCardProps {
  clip: Clip;
  index: number;
}

export const ClipCard: React.FC<ClipCardProps> = ({ clip, index }) => {
  const handlePlayAudio = async () => {
    try {
      console.log('Play audio for clip:', clip.id);
      
      // Create audio element and play the audio file from backend
      const audio = new Audio(`http://localhost:8000/audio/${clip.id}`);
      
      // Add event listeners for better user experience
      audio.addEventListener('loadstart', () => {
        console.log('Loading audio...');
      });
      
      audio.addEventListener('canplay', () => {
        console.log('Audio ready to play');
        audio.play();
      });
      
      audio.addEventListener('error', (e) => {
        console.error('Error playing audio:', e);
        alert('Failed to play audio. Please try again.');
      });
      
      // Load the audio
      audio.load();
      
    } catch (error) {
      console.error('Error playing audio:', error);
      alert('Failed to play audio. Please try again.');
    }
  };

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
            #{index + 1}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              Clip {index + 1}
            </h3>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <ClockIcon className="h-4 w-4" />
              <span>{formatTime(clip.start_time)} - {formatTime(clip.end_time)}</span>
            </div>
          </div>
        </div>
        <ScoreDisplay score={clip.score} size="sm" showLabel={false} />
      </div>

      <div className="space-y-3">
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-1">Transcript</h4>
          <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
            {clip.transcript ? truncateText(clip.transcript, 150) : 'No transcript available'}
          </p>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-1">Why This Score?</h4>
          <p className="text-sm text-gray-600">
            {clip.reasoning}
          </p>
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <button
            onClick={handlePlayAudio}
            className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 transition-colors"
          >
            <PlayIcon className="h-4 w-4" />
            Play Audio
          </button>
          
          <div className="text-xs text-gray-500">
            Duration: {formatTime(clip.end_time - clip.start_time)}
          </div>
        </div>
      </div>
    </div>
  );
};
