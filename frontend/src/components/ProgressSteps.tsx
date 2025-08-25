import React from 'react';
import { CheckCircle2, Circle, Loader2, AlertTriangle } from 'lucide-react';

export type StepStatus = 'pending' | 'active' | 'done' | 'error';

export interface ProgressStep {
  id: string;
  label: string;
  description?: string;
  status: StepStatus;
}

interface ProgressStepsProps {
  steps: ProgressStep[];
  autoAdvance?: boolean;
  onComplete?: () => void;
  ariaLabel?: string;
  size?: 'sm' | 'md';
  isBackendComplete?: boolean; // New prop to control completion
}

const randDelay = () => 8000 + Math.floor(Math.random() * 4000); // 8-12 seconds per step - much slower

export const ProgressSteps: React.FC<ProgressStepsProps> = ({
  steps,
  autoAdvance = true,
  onComplete,
  ariaLabel = 'Progress',
  size = 'md',
  isBackendComplete = false,
}) => {
  const [localSteps, setLocalSteps] = React.useState<ProgressStep[]>(() => steps.map(s => ({ ...s })));
  const stepsRef = React.useRef(localSteps);
  stepsRef.current = localSteps;

  // Sync when external steps change (for non-auto mode)
  React.useEffect(() => {
    if (!autoAdvance) {
      setLocalSteps(steps.map(s => ({ ...s })));
    }
  }, [steps, autoAdvance]);

  // Auto advance flow
  React.useEffect(() => {
    if (!autoAdvance) {
      // When autoAdvance is false, just show the first step as active
      setLocalSteps(prev => {
        const next = prev.map(s => ({ ...s }));
        if (next.every(s => s.status === 'pending')) {
          if (next[0]) next[0].status = 'active';
        }
        return next;
      });
      return;
    }

    // For autoAdvance=true, start with first step active
    setLocalSteps(prev => {
      const next = prev.map(s => ({ ...s }));
      if (next.every(s => s.status === 'pending')) {
        if (next[0]) next[0].status = 'active';
      }
      return next;
    });

    let isCancelled = false;
    // Start: first active
    setLocalSteps(prev => {
      const next = prev.map(s => ({ ...s }));
      if (next.find(s => s.status === 'active')) return next; // already running
      if (next.every(s => s.status === 'pending')) {
        if (next[0]) next[0].status = 'active';
      }
      return next;
    });

    const tick = () => {
      setLocalSteps(prev => {
        const next = prev.map(s => ({ ...s }));
        const activeIdx = next.findIndex(s => s.status === 'active');
        if (activeIdx === -1) return next;
        
        // Only complete the step if backend is done OR we're not on the last step
        if (isBackendComplete || activeIdx < next.length - 1) {
          // complete active
          next[activeIdx].status = 'done';

          // activate next (but only if not the last step or backend is complete)
          if (activeIdx + 1 < next.length) {
            next[activeIdx + 1].status = 'active';
          }
        }
        return next;
      });
    };

    // schedule loop
    const scheduleNext = () => {
      const delay = randDelay();
      const t = window.setTimeout(() => {
        if (isCancelled) return;
        tick();
        // check if finished using ref to get current state
        const doneAll = stepsRef.current.every(s => s.status === 'done' || s.status === 'error');
        if (!doneAll && !isBackendComplete) {
          scheduleNext();
        }
      }, delay);
      return t;
    };

    const timer = scheduleNext();

    return () => {
      isCancelled = true;
      window.clearTimeout(timer);
    };
  }, [autoAdvance]); // Remove localSteps from dependency to prevent re-runs

  // Fire onComplete when all done
  React.useEffect(() => {
    if (localSteps.length > 0 && localSteps.every(s => s.status === 'done')) {
      onComplete?.();
    }
  }, [localSteps, onComplete]);

  const iconSize = size === 'sm' ? 16 : 18;

  const renderIcon = (status: StepStatus, pop: boolean) => {
    const common = `${pop ? 'icon-pop' : ''}`;
    switch (status) {
      case 'active':
        return <Loader2 size={iconSize} className="text-primary-600 dark:text-primary-400 animate-spin" />;
      case 'done':
        return <CheckCircle2 size={iconSize} className={`text-green-600 dark:text-green-400 ${common}`} />;
      case 'error':
        return <AlertTriangle size={iconSize} className="text-amber-600 dark:text-amber-400" />;
      default:
        return <Circle size={iconSize} className="text-slate-400" />;
    }
  };

  const completed = localSteps.filter(s => s.status === 'done').length;
  const total = localSteps.length;

  return (
    <div className="rounded-2xl border border-slate-200/70 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60 shadow-sm p-5">
      <div className="flex items-center gap-3 mb-3">
        <div className="h-5 w-5 rounded-full bg-gradient-to-r from-[#6E7BFF] via-[#9B5DE5] to-[#F15BB5] shadow-sm" />
        <div>
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Processing Your Video</h3>
          <span className="sr-only" aria-live="polite">{completed} of {total} completed</span>
        </div>
      </div>

      <div role="list" aria-label={ariaLabel} className="space-y-1">
        {localSteps.map((step, idx) => {
          const isFirst = idx === 0;
          const isActive = step.status === 'active';
          const isDone = step.status === 'done';
          const pop = isDone; // trigger pop when done
          return (
            <div
              key={step.id}
              role="listitem"
              className={`grid grid-cols-[24px_1fr] gap-3 items-start py-2 ${!isFirst ? 'border-t border-slate-200/60 dark:border-slate-800' : ''} ${isActive ? 'relative before:absolute before:left-[-12px] before:top-0 before:h-full before:w-[3px] before:rounded-full before:bg-gradient-to-b before:from-[#6E7BFF] before:via-[#9B5DE5] before:to-[#F15BB5]' : ''}`}
            >
              <div className="mt-0.5">
                {renderIcon(step.status, pop)}
              </div>
              <div className={`transition-all duration-300 ${isActive ? 'opacity-100 translate-y-0' : 'opacity-90'} `}>
                <div aria-live={isActive ? 'polite' : undefined} className="text-slate-800 dark:text-slate-100 font-medium">
                  {step.label}
                </div>
                {step.description && (
                  <div className="text-slate-500 dark:text-slate-400 text-sm">{step.description}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressSteps;


