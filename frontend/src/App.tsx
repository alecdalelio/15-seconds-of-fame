import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { VideoProcessor } from './components/VideoProcessor';
import { ClipLibrary } from './components/ClipLibrary';
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

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        {/* Simple Navigation */}
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold text-gray-900">15 Seconds of Fame</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setCurrentView('processor')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentView === 'processor' 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Create Clips
                </button>
                <button
                  onClick={() => setCurrentView('library')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentView === 'library' 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  My Library
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="py-8 px-4">
          {currentView === 'processor' && <VideoProcessor />}
          {currentView === 'library' && <ClipLibrary />}
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
