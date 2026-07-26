"use client";

import Link from 'next/link';
import { format } from 'date-fns';
import type { Provider } from '@shared/types/provider';
import ProviderTypeBadge from './ProviderTypeBadge';
import ProviderStatusBadge from './ProviderStatusBadge';
import ProviderHealthBadge from './ProviderHealthBadge';

interface Props {
  provider: Provider;
}

export default function ProviderCard({ provider }: Props) {
  return (
    <div className="group relative flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:shadow-md hover:border-indigo-300 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-indigo-500">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex-1 min-w-0">
          <Link
            href={`/providers/${provider.id}`}
            className="block truncate font-semibold text-slate-800 hover:text-indigo-600 dark:text-slate-100 dark:hover:text-indigo-400"
          >
            {provider.name}
          </Link>
          <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400 truncate">{provider.slug}</p>
        </div>
        <ProviderHealthBadge health={provider.health} />
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-1.5 mb-4">
        <ProviderTypeBadge type={provider.type} />
        <ProviderStatusBadge status={provider.status} />
        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
          provider.environment === 'production'
            ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
            : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
        }`}>
          {provider.environment === 'production' ? '🚀 Prod' : '🧪 Sandbox'}
        </span>
      </div>

      {/* Footer */}
      <div className="mt-auto pt-3 border-t border-slate-100 dark:border-slate-700">
        <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>By {provider.createdBy}</span>
          {provider.lastSync && (
            <span>Sync: {format(new Date(provider.lastSync), 'PP')}</span>
          )}
        </div>
      </div>
    </div>
  );
}
