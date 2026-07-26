"use client";

import clsx from 'clsx';
import type { ProviderHealth } from '@shared/types/provider';

interface Props {
  health: ProviderHealth;
  size?: 'sm' | 'md';
}

const config: Record<ProviderHealth, { label: string; className: string }> = {
  healthy: { label: 'Healthy', className: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200' },
  warning: { label: 'Warning', className: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200' },
  offline: { label: 'Offline', className: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300' },
  error:   { label: 'Error',   className: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' },
};

export default function ProviderHealthBadge({ health, size = 'sm' }: Props) {
  const { label, className } = config[health];
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 rounded-full font-medium',
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm',
        className,
      )}
    >
      <span className={clsx('h-1.5 w-1.5 rounded-full', {
        'bg-emerald-500': health === 'healthy',
        'bg-amber-500':   health === 'warning',
        'bg-slate-400':   health === 'offline',
        'bg-red-500':     health === 'error',
      })} />
      {label}
    </span>
  );
}
