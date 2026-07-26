"use client";

import { ChangeEvent } from 'react';
import type { ProviderStatus, ProviderType } from '@shared/types/provider';

interface Filters {
  status: ProviderStatus | '';
  type: ProviderType | '';
}

interface Props {
  filters: Filters;
  onChange: (filters: Filters) => void;
}

const STATUS_OPTIONS: Array<{ value: ProviderStatus | ''; label: string }> = [
  { value: '', label: 'All Statuses' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'maintenance', label: 'Maintenance' },
  { value: 'archived', label: 'Archived' },
];

const TYPE_OPTIONS: Array<{ value: ProviderType | ''; label: string }> = [
  { value: '', label: 'All Types' },
  { value: 'flights', label: '✈ Flights' },
  { value: 'hotels', label: '🏨 Hotels' },
  { value: 'cars', label: '🚗 Cars' },
  { value: 'transfers', label: '🚌 Transfers' },
  { value: 'activities', label: '🎯 Activities' },
  { value: 'insurance', label: '🛡 Insurance' },
  { value: 'visa', label: '📄 Visa' },
  { value: 'packages', label: '📦 Packages' },
];

export default function ProviderFilters({ filters, onChange }: Props) {
  const handleStatus = (e: ChangeEvent<HTMLSelectElement>) =>
    onChange({ ...filters, status: e.target.value as ProviderStatus | '' });

  const handleType = (e: ChangeEvent<HTMLSelectElement>) =>
    onChange({ ...filters, type: e.target.value as ProviderType | '' });

  const selectClass =
    'rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200';

  return (
    <div className="flex flex-wrap gap-3 items-center">
      <select id="filter-status" value={filters.status} onChange={handleStatus} className={selectClass}>
        {STATUS_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
      <select id="filter-type" value={filters.type} onChange={handleType} className={selectClass}>
        {TYPE_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}
