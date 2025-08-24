import React from 'react';

interface ScoreDisplayProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ 
  score, 
  size = 'md', 
  showLabel = true 
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600 bg-green-100';
    if (score >= 6) return 'text-blue-600 bg-blue-100';
    if (score >= 4) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreEmoji = (score: number) => {
    if (score >= 8) return '🔥';
    if (score >= 6) return '👍';
    if (score >= 4) return '😐';
    return '😴';
  };

  const sizeClasses = {
    sm: 'text-sm px-2 py-1',
    md: 'text-base px-3 py-2',
    lg: 'text-lg px-4 py-3'
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`inline-flex items-center gap-1 rounded-full font-semibold ${getScoreColor(score)} ${sizeClasses[size]}`}>
        <span>{getScoreEmoji(score)}</span>
        <span>{score.toFixed(1)}</span>
      </div>
      {showLabel && (
        <div className="flex-1">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(score / 10) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
