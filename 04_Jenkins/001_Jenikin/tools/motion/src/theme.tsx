import type {CSSProperties, ReactNode} from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

export const colors = {
  bg: '#f8fafc',
  ink: '#0f172a',
  blue: '#2563eb',
  blueSoft: '#dbeafe',
  green: '#16a34a',
  greenSoft: '#dcfce7',
  amber: '#d97706',
  amberSoft: '#fef3c7',
  red: '#dc2626',
  redSoft: '#fee2e2',
  gray: '#64748b',
  graySoft: '#e2e8f0',
  white: '#ffffff',
};

export const fontFamily = 'Noto Sans Thai, sans-serif';

export const shadow = '0 14px 36px rgba(15, 23, 42, 0.10)';

export const cardStyle: CSSProperties = {
  background: colors.white,
  border: `1px solid ${colors.graySoft}`,
  borderRadius: 22,
  boxShadow: shadow,
};

export const Scene = ({children}: {children: ReactNode}) => (
  <AbsoluteFill
    style={{
      backgroundColor: colors.bg,
      backgroundImage:
        'radial-gradient(circle at 12% 18%, rgba(37,99,235,.08), transparent 28%), radial-gradient(circle at 88% 82%, rgba(22,163,74,.07), transparent 25%)',
      color: colors.ink,
      fontFamily,
      overflow: 'hidden',
    }}
  >
    {children}
  </AbsoluteFill>
);

export const Eyebrow = ({children, color = colors.blue}: {children: ReactNode; color?: string}) => (
  <div
    style={{
      color,
      fontSize: 22,
      fontWeight: 800,
      letterSpacing: 1.2,
      lineHeight: 1.2,
    }}
  >
    {children}
  </div>
);

export const LoopCrossfade = ({render}: {render: (storyFrame: number) => ReactNode}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const blend = interpolate(frame, [durationInFrames - 42, durationInFrames - 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill>
      <AbsoluteFill>{render(0)}</AbsoluteFill>
      <AbsoluteFill style={{opacity: 1 - blend}}>{render(Math.min(frame, durationInFrames - 42))}</AbsoluteFill>
    </AbsoluteFill>
  );
};

export const ArrowHead = ({x, y, color = colors.blue, rotate = 0}: {x: number; y: number; color?: string; rotate?: number}) => (
  <div
    style={{
      position: 'absolute',
      left: x,
      top: y,
      width: 0,
      height: 0,
      borderTop: '8px solid transparent',
      borderBottom: '8px solid transparent',
      borderLeft: `13px solid ${color}`,
      rotate: `${rotate}deg`,
    }}
  />
);

export const StatusDot = ({color, size = 12}: {color: string; size?: number}) => (
  <span style={{display: 'inline-block', width: size, height: size, borderRadius: '50%', background: color}} />
);
