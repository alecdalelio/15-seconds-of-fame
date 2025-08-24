import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { VideoProcessor } from './components/VideoProcessor';
import { ClipLibrary } from './components/ClipLibrary';
import { MediaProvider } from './contexts/MediaContext';
import type { Clip } from './types/api';
import { loadSavedClips, addClipToStorage, removeClipFromStorage, clearAllClips } from './utils/storage';
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

  return (
    <QueryClientProvider client={queryClient}>
      <MediaProvider>
        <div className="min-h-screen bg-gray-50">
          {/* Simple Navigation */}
          <nav className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-14 sm:h-16">
                <div className="flex items-center">
                  <h1 className="text-lg sm:text-xl font-bold text-gray-900">15 Seconds of Fame</h1>
                </div>
                <div className="flex items-center space-x-2 sm:space-x-4">
                  <button
                    onClick={() => setCurrentView('processor')}
                    className={`px-2 sm:px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                      currentView === 'processor' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    Create Clips
                  </button>
                  <button
                    onClick={() => setCurrentView('library')}
                    className={`px-2 sm:px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                      currentView === 'library' 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    My Library
                  </button>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="py-4 sm:py-8 px-4 sm:px-6 lg:px-8">
            {currentView === 'processor' && (
              <VideoProcessor 
                savedClips={savedClips}
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
        </div>
      </MediaProvider>
    </QueryClientProvider>
  );
}

export default App;
