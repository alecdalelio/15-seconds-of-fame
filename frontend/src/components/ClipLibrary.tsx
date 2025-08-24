import React, { useState } from 'react';
import { PlayIcon, TrashIcon, HeartIcon, PlusIcon, VideoCameraIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import type { Clip } from '../types/api';
import { formatTime, truncateText } from '../utils/validation';
import { getVideoIdentifier } from '../utils/video';
import { ViralAnalysisDisplay } from './ViralAnalysisDisplay';

interface Video {
  id: string;
  title: string;
  url: string;
  processed_at: string;
  clips: Clip[];
}

interface ClipLibraryProps {
  savedClips: Clip[];
  onRemoveClip: (clipId: string) => void;
  onClearAll?: () => void;
}

export const ClipLibrary: React.FC<ClipLibraryProps> = ({ savedClips, onRemoveClip, onClearAll }) => {
  // In a real app, this would come from a database or localStorage
  const [videos, setVideos] = useState<Video[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'ai' | 'manual'>('all');
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null);
  const [showClipCreator, setShowClipCreator] = useState(false);
  const [expandedClips, setExpandedClips] = useState<Set<string>>(new Set());

  // Use saved clips from props instead of videos
  const filteredClips = savedClips.filter(clip => {
    const matchesSearch = 
      clip.transcript?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      clip.reasoning?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      clip.title?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterType === 'all' || 
      (filterType === 'ai' && clip.ai_generated) ||
      (filterType === 'manual' && !clip.ai_generated);
    
    return matchesSearch && matchesFilter;
  });

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
    onRemoveClip(clipId);
  };

  const toggleClipExpansion = (clipId: string) => {
    setExpandedClips(prev => {
      const newSet = new Set(prev);
      if (newSet.has(clipId)) {
        newSet.delete(clipId);
      } else {
        newSet.add(clipId);
      }
      return newSet;
    });
  };

  const handleCreateClip = (video: Video) => {
    setSelectedVideo(video);
    setShowClipCreator(true);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          My Viral Clips Library
        </h1>
        <p className="text-gray-600">
          Save and organize your favorite viral clips, both AI-generated and custom-created
        </p>
      </div>

              {/* Search and Filters */}
        <div className="flex items-center justify-between">
          <div className="flex-1 max-w-md">
            <input
              type="text"
              placeholder="Search clips by transcript, reasoning, or video title..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center gap-4">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as 'all' | 'ai' | 'manual')}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Clips</option>
              <option value="ai">AI Generated</option>
              <option value="manual">Manual Clips</option>
            </select>
            <div className="text-sm text-gray-500">
              {filteredClips.length} of {savedClips.length} clips
            </div>
            {savedClips.length > 0 && onClearAll && (
              <button
                onClick={onClearAll}
                className="px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
              >
                Clear All
              </button>
            )}
          </div>
        </div>

      {/* Videos Section */}
      {videos.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Your Videos</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {videos.map((video) => (
              <div key={video.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <VideoCameraIcon className="h-5 w-5 text-blue-600" />
                    <h3 className="font-medium text-gray-900 line-clamp-2">{video.title}</h3>
                  </div>
                  <button
                    onClick={() => handleCreateClip(video)}
                    className="text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    <PlusIcon className="h-5 w-5" />
                  </button>
                </div>
                
                <div className="space-y-2">
                  <p className="text-sm text-gray-500">
                    {video.clips.length} clips • {new Date(video.processed_at).toLocaleDateString()}
                  </p>
                  <div className="flex gap-2">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                      {video.clips.filter(c => c.ai_generated).length} AI
                    </span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                      {video.clips.filter(c => !c.ai_generated).length} Manual
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clips Section */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">All Clips</h2>
        
        {savedClips.length === 0 ? (
          <div className="text-center py-12">
            <HeartIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No clips yet</h3>
            <p className="text-gray-500">
              Process a YouTube video to get started, or create custom clips from your videos.
            </p>
          </div>
        ) : filteredClips.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No clips found</h3>
            <p className="text-gray-500">
              Try adjusting your search terms or filters.
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
                    <div className="flex flex-col">
                      <span className="text-sm text-gray-500">
                        {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
                      </span>
                      <span className="text-xs text-gray-400">
                        Duration: {formatTime(clip.end_time - clip.start_time)}
                      </span>
                    </div>
                    {clip.ai_generated ? (
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">AI Generated</span>
                    ) : (
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">Manual</span>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveClip(clip.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>

                <div className="space-y-3">
                  {/* Clip Title and Score */}
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">
                        {clip.title || 'Untitled Clip'}
                      </h4>
                      <p className="text-xs text-gray-500">
                        From: {getVideoIdentifier(clip.video_title || '', clip.video_source)}
                      </p>
                      {clip.video_source && (
                        <a 
                          href={clip.video_source} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:text-blue-700 underline"
                        >
                          View Original Video
                        </a>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-blue-600">
                        {clip.score?.toFixed(1) || clip.combined_score?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="text-xs text-gray-500">Viral Score</div>
                    </div>
                  </div>
                  
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

                  {/* Suggested Caption */}
                  {clip.suggested_caption && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Suggested Caption</h4>
                      <p className="text-sm text-gray-600 bg-blue-50 rounded p-2 border border-blue-200">
                        {clip.suggested_caption}
                      </p>
                    </div>
                  )}

                  {/* Viral Analysis Toggle */}
                  {(clip.viral_score || clip.combined_score) && (
                    <div>
                      <button
                        onClick={() => toggleClipExpansion(clip.id)}
                        className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
                      >
                        {expandedClips.has(clip.id) ? (
                          <ChevronUpIcon className="h-4 w-4" />
                        ) : (
                          <ChevronDownIcon className="h-4 w-4" />
                        )}
                        {expandedClips.has(clip.id) ? 'Hide' : 'Show'} Detailed Analysis
                      </button>
                      
                      {expandedClips.has(clip.id) && (
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

      {/* Clip Creator Modal */}
      {showClipCreator && selectedVideo && (
        <ClipCreator 
          video={selectedVideo}
          onClose={() => setShowClipCreator(false)}
          onClipCreated={(newClip) => {
            setVideos(prev => prev.map(video => 
              video.id === selectedVideo.id 
                ? { ...video, clips: [...video.clips, newClip] }
                : video
            ));
            setShowClipCreator(false);
          }}
        />
      )}
    </div>
  );
};

// Clip Creator Component (to be implemented)
interface ClipCreatorProps {
  video: Video;
  onClose: () => void;
  onClipCreated: (clip: Clip) => void;
}

const ClipCreator: React.FC<ClipCreatorProps> = ({ video, onClose, onClipCreated }) => {
  // This would be a sophisticated timeline interface
  // For now, just a placeholder
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Create Custom Clip from "{video.title}"</h3>
        <p className="text-gray-600 mb-4">
          Interactive timeline interface would go here for selecting start/end times.
        </p>
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              // This would create a clip with the selected time range
              const newClip: Clip = {
                id: `manual-${Date.now()}`,
                segment_id: `manual-${Date.now()}`,
                score: 7.5,
                start_time: 0,
                end_time: 15,
                transcript: "Custom clip transcript",
                audio_path: "",
                video_path: "",
                reasoning: "Custom clip with AI-generated caption",
                ai_generated: false,
                title: "Custom Clip",
                duration: "15s"
              };
              onClipCreated(newClip);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Clip
          </button>
        </div>
      </div>
    </div>
  );
};
