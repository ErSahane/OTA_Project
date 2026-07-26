"use client";

import type { ProviderStats } from '@shared/types/provider';
import { ServerIcon, CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon } from '@heroicons/react/24/outline';

interface Props {
  stats: ProviderStats;
}

export default function ProviderStats({ stats }: Props) {
  const items = [
    { label: 'Total', value: stats.total, icon: <ServerIcon className="h-5 w-5 text-slate-500" />, color: 'bg-slate-100 dark:bg-slate-800' },
    { label: 'Active', value: stats.active, icon: <CheckCircleIcon className="h-5 w-5 text-emerald-500" />, color: 'bg-emerald-50 dark:bg-emerald-900/20' },
    { label: 'Healthy', value: stats.healthy, icon: <CheckCircleIcon className="h-5 w-5 text-emerald-400" />, color: 'bg-emerald-50 dark:bg-emerald-900/20' },
    { label: 'Warning', value: stats.warning, icon: <ExclamationTriangleIcon className="h-5 w-5 text-amber-500" />, color: 'bg-amber-50 dark:bg-amber-900/20' },
    { label: 'Offline', value: stats.offline, icon: <XCircleIcon className="h-5 w-5 text-slate-400" />, color: 'bg-slate-100 dark:bg-slate-800' },
    { label: 'Error', value: stats.error, icon: <XCircleIcon className="h-5 w-5 text-red-500" />, color: 'bg-red-50 dark:bg-red-900/20' },
    { label: 'Maintenance', value: stats.maintenance, icon: <ExclamationTriangleIcon className="h-5 w-5 text-amber-400" />, color: 'bg-amber-50 dark:bg-amber-900/20' },
    { label: 'Archived', value: stats.archived, icon: <XCircleIcon className="h-5 w-5 text-slate-300" />, color: 'bg-slate-100 dark:bg-slate-800' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
      {items.map((item) => (
        <div key={item.label} className={`rounded-xl p-3 flex flex-col items-center justify-center gap-1 ${item.color}`}>
          {item.icon}
          <span className="text-xl font-bold text-slate-800 dark:text-slate-100">{item.value}</span>
          <span className="text-xs text-slate-500 dark:text-slate-400">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
