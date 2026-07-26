"use client";

import { format } from 'date-fns';
import type { AuditLogEntry } from '@shared/types/provider';

interface Props {
  entries: AuditLogEntry[];
}

const ACTION_CONFIG: Record<AuditLogEntry['action'], { label: string; color: string }> = {
  create:             { label: 'Created',           color: 'bg-emerald-500' },
  update:             { label: 'Updated',           color: 'bg-indigo-500' },
  delete:             { label: 'Deleted',           color: 'bg-red-500' },
  credential_change:  { label: 'Credentials Changed', color: 'bg-amber-500' },
  environment_change: { label: 'Environment Changed', color: 'bg-violet-500' },
  status_change:      { label: 'Status Changed',    color: 'bg-blue-500' },
  connection_test:    { label: 'Connection Tested', color: 'bg-teal-500' },
  restore:            { label: 'Restored',          color: 'bg-emerald-400' },
};

export default function AuditTimeline({ entries }: Props) {
  if (entries.length === 0) {
    return (
      <div className="py-10 text-center text-slate-400 dark:text-slate-600">
        <p className="text-4xl mb-2">📋</p>
        <p className="text-sm">No audit events recorded yet.</p>
      </div>
    );
  }

  return (
    <ol className="relative border-l-2 border-slate-200 dark:border-slate-700 ml-3 space-y-6">
      {entries.map((entry) => {
        const cfg = ACTION_CONFIG[entry.action];
        return (
          <li key={entry.id} className="ml-6">
            <span className={`absolute -left-[9px] mt-1 flex h-4 w-4 items-center justify-center rounded-full ${cfg.color}`} />
            <div className="rounded-xl border border-slate-100 bg-white px-4 py-3 dark:border-slate-700 dark:bg-slate-800">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                <span className="text-sm font-medium text-slate-800 dark:text-slate-100">{cfg.label}</span>
                <time className="text-xs text-slate-400 dark:text-slate-500">
                  {format(new Date(entry.timestamp), 'PPpp')}
                </time>
              </div>
              <div className="flex flex-wrap gap-3 text-xs text-slate-500 dark:text-slate-400">
                <span>👤 {entry.user}</span>
                {entry.ip && <span>🌐 {entry.ip}</span>}
                {entry.details && <span className="italic">{entry.details}</span>}
              </div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
