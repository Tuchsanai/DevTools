import {colors} from '../theme';

export const CheckIcon = ({size = 24, color = colors.green}: {size?: number; color?: string}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <path d="M5 12.5 9.2 17 19 7" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const GitCommitIcon = ({color = colors.blue}: {color?: string}) => (
  <svg width="46" height="46" viewBox="0 0 48 48" fill="none" aria-hidden="true">
    <path d="M4 24h13M31 24h13" stroke={color} strokeWidth="4" strokeLinecap="round" />
    <circle cx="24" cy="24" r="8" fill="white" stroke={color} strokeWidth="4" />
  </svg>
);

export const JenkinsNode = ({color = colors.blue}: {color?: string}) => (
  <svg width="60" height="60" viewBox="0 0 60 60" fill="none" aria-hidden="true">
    <rect x="8" y="7" width="44" height="46" rx="12" fill="white" stroke={color} strokeWidth="3" />
    <path d="M20 23h20M20 31h20M20 39h12" stroke={color} strokeWidth="3" strokeLinecap="round" />
    <circle cx="43" cy="39" r="4" fill={colors.green} />
  </svg>
);

export const Gear = ({size, rotation, color}: {size: number; rotation: number; color: string}) => (
  <svg width={size} height={size} viewBox="0 0 100 100" aria-hidden="true" style={{rotate: `${rotation}deg`}}>
    <g fill={color}>
      {Array.from({length: 10}).map((_, index) => (
        <rect key={index} x="43" y="1" width="14" height="24" rx="4" transform={`rotate(${index * 36} 50 50)`} />
      ))}
      <circle cx="50" cy="50" r="35" />
    </g>
    <circle cx="50" cy="50" r="14" fill={colors.bg} />
  </svg>
);

export const DockerBoxIcon = ({color = colors.blue}: {color?: string}) => (
  <svg width="72" height="54" viewBox="0 0 72 54" fill="none" aria-hidden="true">
    {[0, 1, 2].map((row) =>
      Array.from({length: row === 0 ? 2 : 3}).map((_, column) => (
        <rect key={`${row}-${column}`} x={12 + column * 13 + (row === 0 ? 13 : 0)} y={5 + row * 13} width="10" height="10" rx="2" fill={color} />
      )),
    )}
    <path d="M5 33h54c-2 9-10 15-25 15C17 48 8 43 5 33Z" fill={color} opacity=".18" stroke={color} strokeWidth="2.5" />
    <path d="M58 28c6-4 9 0 9 0-2 5-6 6-11 6" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
  </svg>
);
