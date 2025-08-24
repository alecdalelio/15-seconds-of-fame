import React from 'react';
import { FireIcon, StarIcon, SparklesIcon } from '@heroicons/react/24/outline';

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
    if (score >= 8.0) return 'text-success-700 bg-success-100 border-success-200';
    if (score >= 6.0) return 'text-primary-700 bg-primary-100 border-primary-200';
    if (score >= 4.0) return 'text-accent-700 bg-accent-100 border-accent-200';
    return 'text-gray-700 bg-gray-100 border-gray-200';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 8.0) return <FireIcon className="w-4 h-4" />;
    if (score >= 6.0) return <StarIcon className="w-4 h-4" />;
    if (score >= 4.0) return <SparklesIcon className="w-4 h-4" />;
    return <SparklesIcon className="w-4 h-4" />;
  };

  const getScoreLabel = (score: number) => {
    if (score >= 8.0) return 'Viral';
    if (score >= 6.0) return 'High';
    if (score >= 4.0) return 'Medium';
    return 'Low';
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  };

  const iconSizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`inline-flex items-center gap-1.5 rounded-xl font-bold border ${getScoreColor(score)} ${sizeClasses[size]} shadow-soft`}>
        <div className={iconSizeClasses[size]}>
          {getScoreIcon(score)}
        </div>
        <span>{score.toFixed(1)}</span>
        {size !== 'sm' && (
          <span className="text-xs opacity-75">{getScoreLabel(score)}</span>
        )}
      </div>
      {showLabel && (
        <div className="flex-1 min-w-0">
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-2 rounded-full transition-all duration-500 ${
                score >= 8.0 ? 'bg-gradient-to-r from-success-400 to-success-600' :
                score >= 6.0 ? 'bg-gradient-to-r from-primary-400 to-primary-600' :
                score >= 4.0 ? 'bg-gradient-to-r from-accent-400 to-accent-600' :
                'bg-gradient-to-r from-gray-400 to-gray-600'
              }`}
              style={{ width: `${(score / 10) * 100}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
