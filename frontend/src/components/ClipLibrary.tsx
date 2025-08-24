import React, { useState } from 'react';
import { PlayIcon, TrashIcon, HeartIcon } from '@heroicons/react/24/outline';
import type { Clip } from '../types/api';
import { formatTime, truncateText } from '../utils/validation';

export const ClipLibrary: React.FC = () => {
  // In a real app, this would come from a database or localStorage
  const [savedClips, setSavedClips] = useState<Clip[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  const handlePlayAudio = async (clipId: string) => {
    try {
      const audio = new Audio(`http://localhost:8000/audio/${clipId}`);
      audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
      alert('Failed to play audio. Please try again.');
    }
  };

  const handleRemoveClip = (clipId: string) => {
    setSavedClips(prev => prev.filter(clip => clip.id !== clipId));
  };

  const filteredClips = savedClips.filter(clip =>
    clip.transcript?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    clip.reasoning?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          My Viral Clips Library
        </h1>
        <p className="text-gray-600">
          Save and organize your favorite viral clips for easy access
        </p>
      </div>

      {/* Search and Stats */}
      <div className="flex items-center justify-between">
        <div className="flex-1 max-w-md">
          <input
            type="text"
            placeholder="Search clips by transcript or reasoning..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="text-sm text-gray-500">
          {filteredClips.length} of {savedClips.length} clips
        </div>
      </div>

      {/* Clips Grid */}
      {savedClips.length === 0 ? (
        <div className="text-center py-12">
          <HeartIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No saved clips yet</h3>
          <p className="text-gray-500">
            Process a YouTube video and save your favorite clips to build your library.
          </p>
        </div>
      ) : filteredClips.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No clips found</h3>
          <p className="text-gray-500">
            Try adjusting your search terms.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredClips.map((clip, index) => (
            <div key={clip.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">
                    {index + 1}
                  </div>
                  <span className="text-sm text-gray-500">
                    {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
                  </span>
                </div>
                <button
                  onClick={() => handleRemoveClip(clip.id)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>

              <div className="space-y-3">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Transcript</h4>
                  <p className="text-sm text-gray-600 bg-gray-50 rounded p-2">
                    {clip.transcript ? truncateText(clip.transcript, 120) : 'No transcript available'}
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Viral Reasoning</h4>
                  <p className="text-sm text-gray-600">
                    {clip.reasoning}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                  <button
                    onClick={() => handlePlayAudio(clip.id)}
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    <PlayIcon className="h-4 w-4" />
                    Play
                  </button>
                  
                  <div className="text-xs text-gray-500">
                    {formatTime(clip.end_time - clip.start_time)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
