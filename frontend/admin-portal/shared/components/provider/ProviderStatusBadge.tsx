"use client";

import clsx from 'clsx';
import type { ProviderStatus } from '@shared/types/provider';

interface Props {
  status: ProviderStatus;
}

const config: Record<ProviderStatus, { label: string; className: string }> = {
  active:      { label: 'Active',      className: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200' },
  inactive:    { label: 'Inactive',    className: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300' },
  maintenance: { label: 'Maintenance', className: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200' },
  archived:    { label: 'Archived',    className: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300' },
};

export default function ProviderStatusBadge({ status }: Props) {
  const { label, className } = config[status];
  return (
    <span className={clsx('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', className)}>
      {label}
    </span>
  );
}
