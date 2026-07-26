"use client";

import clsx from 'clsx';
import type { ProviderType } from '@shared/types/provider';

interface Props {
  type: ProviderType;
}

const config: Record<ProviderType, { label: string; className: string }> = {
  flights:    { label: '✈ Flights',    className: 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-200' },
  hotels:     { label: '🏨 Hotels',     className: 'bg-violet-100 text-violet-800 dark:bg-violet-900 dark:text-violet-200' },
  cars:       { label: '🚗 Cars',       className: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' },
  transfers:  { label: '🚌 Transfers',  className: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200' },
  activities: { label: '🎯 Activities', className: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200' },
  insurance:  { label: '🛡 Insurance',  className: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200' },
  visa:       { label: '📄 Visa',       className: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' },
  packages:   { label: '📦 Packages',   className: 'bg-lime-100 text-lime-800 dark:bg-lime-900 dark:text-lime-200' },
};

export default function ProviderTypeBadge({ type }: Props) {
  const { label, className } = config[type];
  return (
    <span className={clsx('inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium', className)}>
      {label}
    </span>
  );
}
