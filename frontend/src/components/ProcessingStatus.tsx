import React, { useState, useEffect } from 'react';

interface ProcessingStatusProps {
  isProcessing: boolean;
  currentStep: number;
}

interface AnimatedStepProps {
  label: string;
  isActive: boolean;
  isCompleted: boolean;
}

const AnimatedStep: React.FC<AnimatedStepProps> = ({ label, isActive, isCompleted }) => {
  const [displayText, setDisplayText] = useState('');
  const [showCursor, setShowCursor] = useState(false);

  useEffect(() => {
    if (!isActive && !isCompleted) {
      setDisplayText('');
      setShowCursor(false);
      return;
    }

    if (isCompleted) {
      setDisplayText(label);
      setShowCursor(false);
      return;
    }

    // Typewriter effect for active step
    setDisplayText('');
    setShowCursor(true);

    let currentIndex = 0;
    const typeInterval = setInterval(() => {
      if (currentIndex < label.length) {
        setDisplayText(label.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        setShowCursor(false);
        clearInterval(typeInterval);
      }
    }, 50); // Adjust speed as needed

    return () => clearInterval(typeInterval);
  }, [isActive, isCompleted, label]);

  const dotClass = () => {
    if (isCompleted) return 'bg-green-500';
    if (isActive) return 'bg-blue-500 animate-pulse';
    return 'bg-gray-300';
  };

  return (
    <div className="flex items-center text-sm text-gray-600">
      <div className={`w-2 h-2 rounded-full mr-3 ${dotClass()}`}></div>
      <span className="font-mono">
        {displayText}
        {showCursor && <span className="animate-pulse">|</span>}
      </span>
    </div>
  );
};

const STEPS = [
  'Downloading video from YouTube',
  'Extracting audio and creating segments',
  'Generating transcripts with AI',
  'Analyzing engagement potential',
];

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({ isProcessing, currentStep }) => {
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
          {STEPS.map((label, i) => (
            <AnimatedStep
              key={label}
              label={label}
              isActive={i === currentStep}
              isCompleted={i < currentStep}
            />
          ))}
        </div>
      </div>
    </div>
  );
};
