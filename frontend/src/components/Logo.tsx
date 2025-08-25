import * as React from 'react';
import { useId } from 'react';

export interface LogoProps {
  /** Render size in pixels */
  size?: number; // default 32
  /** Background variant context (controls triangle fill & gradient tuning) */
  variant?: 'light' | 'dark'; // default 'light'
  /** Show the 15° gap implying a timer tick */
  gap?: boolean; // default true
  /** Optional className passed to the root <svg> */
  className?: string;
  /** Accessible name. If provided, logo is announced. Otherwise decorative. */
  ariaLabel?: string;
}

/**
 * 15 Seconds of Fame — Logo
 * Abstract play button inside a circular timer ring.
 * - ViewBox: 0 0 100 100
 * - Ring radius ~42, stroke ≈ 10% (10 units)
 * - Optional 15° missing arc near ~2 o'clock using strokeDasharray/offset
 * - Equilateral triangle play glyph sized to ~55% of inner ring diameter
 */
const Logo: React.FC<LogoProps> = ({
  size = 32,
  variant = 'light',
  gap = true,
  className,
  ariaLabel,
}) => {
  const uid = useId();
  const gradId = `logo-grad-${uid}`;
  const filterId = `logo-shadow-${uid}`;
  const titleId = `logo-title-${uid}`;

  // Geometry (aligned to viewBox units)
  const cx = 50;
  const cy = 50;
  const strokeWidth = 10; // 10% of 100 -> scales with size naturally
  const r = 42; // leaves a small margin within 100x100 viewBox
  const innerRadius = r - strokeWidth / 2; // inner diameter for triangle sizing
  const innerDiameter = innerRadius * 2;

  // Triangle sizing — 55% of inner diameter with padding
  const TRIANGLE_SCALE = 0.55; // exposed constant for easy tuning
  const triSide = innerDiameter * TRIANGLE_SCALE;
  const triHeight = (Math.sqrt(3) / 2) * triSide; // equilateral height
  const innerPadding = 1.5; // tiny padding to prevent collision with ring

  // Triangle points (pointing right), centered at (cx, cy) with padding
  const p1 = `${cx + triSide / 2 - innerPadding},${cy}`; // right vertex
  const p2 = `${cx - triSide / 2 + innerPadding},${cy - triHeight / 2}`; // top-left
  const p3 = `${cx - triSide / 2 + innerPadding},${cy + triHeight / 2}`; // bottom-left
  const triPoints = `${p1} ${p2} ${p3}`;

  // Ring dash math for a 15° gap positioned near ~2 o'clock
  const circumference = 2 * Math.PI * r;
  const gapAngleDeg = 15; // missing arc size
  const gapLen = (gapAngleDeg / 360) * circumference;
  const visibleLen = circumference - gapLen;

  // Center of the gap around ~2 o'clock. With SVG circles, the dash pattern
  // begins at 3 o'clock. 2 o'clock is ~30° counter-clockwise from 3 o'clock.
  const gapCenterDeg = 30; // ~2 o'clock
  const gapStartPos = (gapCenterDeg / 360) * circumference - gapLen / 2;
  
  // Ring rendering logic
  const strokeDasharray = gap ? `${visibleLen} ${gapLen}` : undefined;
  const strokeDashoffset = gap ? -gapStartPos : 0;
  const strokeLinecap = gap ? 'butt' : 'round'; // prevent notch when gap is true

  // Variant-aware colors
  const baseStops = ['#6E7BFF', '#9B5DE5', '#F15BB5'] as const;
  const stops = variant === 'dark' ? baseStops.map((c) => lighten(c, 6)) : baseStops;
  const playFill = variant === 'dark' ? '#FFFFFF' : '#000000';

  // Accessibility
  const labelledProps = ariaLabel
    ? { role: 'img' as const, 'aria-labelledby': titleId }
    : { 'aria-hidden': true };

  // Debug logging in development
  if (import.meta.env.DEV) {
    console.log('Logo debug:', {
      size,
      gap,
      variant,
      innerDiameter: innerDiameter.toFixed(2),
      triSide: triSide.toFixed(2),
      circumference: circumference.toFixed(2),
      gapLen: gapLen.toFixed(2),
      strokeDasharray,
      strokeDashoffset: strokeDashoffset.toFixed(2)
    });
  }

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
      preserveAspectRatio="xMidYMid meet"
      shapeRendering="geometricPrecision"
      focusable={false}
      {...labelledProps}
    >
      {ariaLabel && <title id={titleId}>{ariaLabel}</title>}

      <defs>
        {/* Diagonal multi-stop gradient that scales with the viewBox */}
        <linearGradient id={gradId} x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor={stops[0]} />
          <stop offset="50%" stopColor={stops[1]} />
          <stop offset="100%" stopColor={stops[2]} />
        </linearGradient>

        {/* Subtle drop shadow for triangle for contrast on busy backgrounds */}
        <filter id={filterId} x="-20%" y="-20%" width="140%" height="140%" colorInterpolationFilters="sRGB">
          {/* Using feDropShadow keeps the stack simple & crisp at small sizes */}
          <feDropShadow dx="0" dy="1" stdDeviation="1.2" floodOpacity="0.35" />
        </filter>
      </defs>

      {/* Timer ring (optional 15° gap) */}
      <circle
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke={`url(#${gradId})`}
        strokeWidth={strokeWidth}
        strokeLinecap={strokeLinecap}
        strokeLinejoin="round"
        strokeDasharray={strokeDasharray}
        strokeDashoffset={strokeDashoffset}
      />

      {/* Play glyph */}
      <polygon points={triPoints} fill={playFill} filter={`url(#${filterId})`} />
    </svg>
  );
};

// Slight brighten utility (5–6%) for dark variant gradient tuning
function lighten(hex: string, pct = 6): string {
  const clamp = (n: number) => Math.max(0, Math.min(255, Math.round(n)));
  const norm = hex.replace('#', '');
  const r = parseInt(norm.slice(0, 2), 16);
  const g = parseInt(norm.slice(2, 4), 16);
  const b = parseInt(norm.slice(4, 6), 16);
  const f = 1 + pct / 100;
  const rr = clamp(r * f).toString(16).padStart(2, '0');
  const gg = clamp(g * f).toString(16).padStart(2, '0');
  const bb = clamp(b * f).toString(16).padStart(2, '0');
  return `#${rr}${gg}${bb}`;
}
export default Logo;

