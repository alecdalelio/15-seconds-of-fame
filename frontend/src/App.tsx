import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { VideoProcessor } from './components/VideoProcessor';
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
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <VideoProcessor />
      </div>
    </QueryClientProvider>
  );
}

export default App;
