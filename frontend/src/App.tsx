import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { VideoProcessor } from './components/VideoProcessor';
import { ClipLibrary } from './components/ClipLibrary';
import { MediaProvider } from './contexts/MediaContext';
import type { Clip } from './types/api';
import { loadSavedClips, addClipToStorage, removeClipFromStorage, clearAllClips } from './utils/storage';
import { SparklesIcon, VideoCameraIcon, BookOpenIcon } from '@heroicons/react/24/outline';
import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [currentView, setCurrentView] = useState<'processor' | 'library'>('processor');
  
  // Load saved clips from localStorage on component mount
  const [savedClips, setSavedClips] = useState<Clip[]>(() => loadSavedClips());

  // Persistent state for current video processing
  const [currentVideoUrl, setCurrentVideoUrl] = useState<string>('');
  const [currentVideoResults, setCurrentVideoResults] = useState<Clip[]>([]);
  const [currentVideoTitle, setCurrentVideoTitle] = useState<string>('');

  return (
    <QueryClientProvider client={queryClient}>
      <MediaProvider>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
          {/* Enhanced Navigation */}
          <nav className="bg-white/80 backdrop-blur-md shadow-soft border-b border-gray-200/50 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16 sm:h-20">
                <div className="flex items-center">
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center shadow-glow">
                        <SparklesIcon className="w-6 h-6 text-white" />
                      </div>
                      <div className="absolute -top-1 -right-1 w-3 h-3 bg-accent-500 rounded-full animate-pulse-slow"></div>
                    </div>
                    <div>
                      <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                        15 Seconds of Fame
                      </h1>
                      <p className="text-xs text-gray-500 hidden sm:block">AI-Powered Viral Clip Creator</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-1 sm:space-x-2">
                  <button
                    onClick={() => setCurrentView('processor')}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 relative group ${
                      currentView === 'processor' 
                        ? 'bg-primary-100 text-primary-700 shadow-soft' 
                        : 'text-gray-600 hover:text-primary-600 hover:bg-primary-50'
                    }`}
                  >
                    <VideoCameraIcon className="w-4 h-4" />
                    <span className="hidden sm:inline">Create Clips</span>
                    <span className="sm:hidden">Create</span>
                    {currentVideoResults.length > 0 && (
                      <span className="absolute -top-1 -right-1 h-3 w-3 bg-success-500 rounded-full animate-bounce-gentle"></span>
                    )}
                  </button>
                  <button
                    onClick={() => setCurrentView('library')}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                      currentView === 'library' 
                        ? 'bg-secondary-100 text-secondary-700 shadow-soft' 
                        : 'text-gray-600 hover:text-secondary-600 hover:bg-secondary-50'
                    }`}
                  >
                    <BookOpenIcon className="w-4 h-4" />
                    <span className="hidden sm:inline">My Library</span>
                    <span className="sm:hidden">Library</span>
                    {savedClips.length > 0 && (
                      <span className="ml-1 px-2 py-0.5 text-xs bg-secondary-100 text-secondary-700 rounded-full">
                        {savedClips.length}
                      </span>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="py-6 sm:py-8 px-4 sm:px-6 lg:px-8 animate-fade-in">
            {currentView === 'processor' && (
              <VideoProcessor 
                savedClips={savedClips}
                currentVideoUrl={currentVideoUrl}
                currentVideoResults={currentVideoResults}
                currentVideoTitle={currentVideoTitle}
                onVideoProcessed={(url, results, title) => {
                  setCurrentVideoUrl(url);
                  setCurrentVideoResults(results);
                  setCurrentVideoTitle(title);
                }}
                onClearResults={() => {
                  setCurrentVideoUrl('');
                  setCurrentVideoResults([]);
                  setCurrentVideoTitle('');
                }}
                onSaveClip={(clip) => {
                  const newClips = addClipToStorage(clip);
                  setSavedClips(newClips);
                }}
                onRemoveClip={(clipId) => {
                  const newClips = removeClipFromStorage(clipId);
                  setSavedClips(newClips);
                }}
              />
            )}
            {currentView === 'library' && (
              <ClipLibrary 
                savedClips={savedClips}
                onRemoveClip={(clipId) => {
                  const newClips = removeClipFromStorage(clipId);
                  setSavedClips(newClips);
                }}
                onClearAll={() => {
                  clearAllClips();
                  setSavedClips([]);
                }}
              />
            )}
          </main>

          {/* Footer */}
          <footer className="mt-auto py-6 px-4 sm:px-6 lg:px-8 border-t border-gray-200/50 bg-white/50 backdrop-blur-sm">
            <div className="max-w-7xl mx-auto text-center">
              <p className="text-sm text-gray-500">
                Powered by AI • Transform any video into viral 15-second clips
              </p>
            </div>
          </footer>
        </div>
      </MediaProvider>
    </QueryClientProvider>
  );
}

export default App;
