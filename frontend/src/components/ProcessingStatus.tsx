import React from 'react';


interface ProcessingStatusProps {
  isProcessing: boolean;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ isProcessing }) => {
  if (!isProcessing) return null;

  return (
    <div className="card">
      <div className="p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mr-3"></div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Processing Your Video
            </h3>
            <p className="text-gray-600 mt-1">
              This may take a few minutes. We're downloading, analyzing, and scoring your content...
            </p>
          </div>
        </div>
        
        <div className="mt-6 space-y-3">
          <div className="flex items-center text-sm text-gray-600">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
            <span>Downloading video from YouTube</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-3 animate-pulse"></div>
            <span>Extracting audio and creating segments</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <div className="w-2 h-2 bg-gray-300 rounded-full mr-3"></div>
            <span>Generating transcripts with AI</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <div className="w-2 h-2 bg-gray-300 rounded-full mr-3"></div>
            <span>Analyzing engagement potential</span>
          </div>
        </div>
      </div>
    </div>
  );
};
