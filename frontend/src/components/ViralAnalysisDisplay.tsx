import React from 'react';
import { 
  ChartBarIcon, 
  HeartIcon, 
  ExclamationTriangleIcon, 
  UserGroupIcon, 
  AcademicCapIcon, 
  FilmIcon 
} from '@heroicons/react/24/outline';

interface ViralAnalysisDisplayProps {
  viral_score?: number;
  emotional_intensity?: number;
  controversy_level?: number;
  relatability?: number;
  educational_value?: number;
  entertainment_factor?: number;
  combined_score?: number;
  viral_reasoning?: string;
}

interface ScoreItemProps {
  label: string;
  score: number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

const ScoreItem: React.FC<ScoreItemProps> = ({ label, score, icon: Icon, color }) => {
  // Map text colors to background colors
  const getBgColor = (textColor: string) => {
    const colorMap: { [key: string]: string } = {
      'text-red-500': 'bg-red-500',
      'text-pink-500': 'bg-pink-500',
      'text-orange-500': 'bg-orange-500',
      'text-blue-500': 'bg-blue-500',
      'text-green-500': 'bg-green-500',
      'text-purple-500': 'bg-purple-500',
    };
    return colorMap[textColor] || 'bg-gray-500';
  };

  return (
    <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-2">
        <Icon className={`h-4 w-4 ${color}`} />
        <span className="text-sm font-medium text-gray-700">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`h-full ${getBgColor(color)} transition-all duration-300`}
            style={{ width: `${(score / 10) * 100}%` }}
          />
        </div>
        <span className="text-sm font-semibold text-gray-900 min-w-[2rem] text-right">
          {score.toFixed(1)}
        </span>
      </div>
    </div>
  );
};

export const ViralAnalysisDisplay: React.FC<ViralAnalysisDisplayProps> = ({
  viral_score = 0,
  emotional_intensity = 0,
  controversy_level = 0,
  relatability = 0,
  educational_value = 0,
  entertainment_factor = 0,
  combined_score = 0,
  viral_reasoning = ''
}) => {
  const scores = [
    { label: 'Viral Potential', score: viral_score, icon: ChartBarIcon, color: 'text-red-500' },
    { label: 'Emotional Intensity', score: emotional_intensity, icon: HeartIcon, color: 'text-pink-500' },
    { label: 'Controversy Level', score: controversy_level, icon: ExclamationTriangleIcon, color: 'text-orange-500' },
    { label: 'Relatability', score: relatability, icon: UserGroupIcon, color: 'text-blue-500' },
    { label: 'Educational Value', score: educational_value, icon: AcademicCapIcon, color: 'text-green-500' },
    { label: 'Entertainment Factor', score: entertainment_factor, icon: FilmIcon, color: 'text-purple-500' },
  ];

  return (
    <div className="space-y-4">
      {/* Combined Score */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg p-4 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">AI Viral Analysis</h3>
            <p className="text-gray-600 text-sm">Combined viral potential score</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-gray-800">{combined_score.toFixed(1)}</div>
            <div className="text-gray-600 text-sm">/ 10</div>
          </div>
        </div>
      </div>

      {/* Individual Scores */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700">Score Breakdown</h4>
        {scores.map((item) => (
          <ScoreItem key={item.label} {...item} />
        ))}
      </div>

      {/* Viral Reasoning */}
      {viral_reasoning && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Viral Reasoning</h4>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm text-blue-800 leading-relaxed">
              {viral_reasoning}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
