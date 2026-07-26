"use client";

import { useState } from 'react';
import type { ProviderEnvironment } from '@shared/types/provider';
import ConfirmDialog from './ConfirmDialog';

interface Props {
  current: ProviderEnvironment;
  onSwitch: (env: ProviderEnvironment) => Promise<void>;
  disabled?: boolean;
}

export default function EnvironmentSwitcher({ current, onSwitch, disabled = false }: Props) {
  const [pending, setPending] = useState<ProviderEnvironment | null>(null);
  const [loading, setLoading] = useState(false);

  const target: ProviderEnvironment = current === 'sandbox' ? 'production' : 'sandbox';

  const handleConfirm = async () => {
    if (!pending) return;
    setLoading(true);
    try {
      await onSwitch(pending);
    } finally {
      setLoading(false);
      setPending(null);
    }
  };

  return (
    <>
      <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Active Environment</p>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Currently using{' '}
            <span className={`font-semibold ${current === 'production' ? 'text-indigo-600' : 'text-slate-600'}`}>
              {current === 'production' ? '🚀 Production' : '🧪 Sandbox'}
            </span>
          </p>
        </div>
        <button
          onClick={() => setPending(target)}
          disabled={disabled || loading}
          className={`rounded-lg px-4 py-2 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed ${
            target === 'production'
              ? 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-400'
              : 'bg-slate-200 text-slate-700 hover:bg-slate-300 focus:ring-slate-400 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          Switch to {target === 'production' ? '🚀 Production' : '🧪 Sandbox'}
        </button>
      </div>

      <ConfirmDialog
        open={pending !== null}
        title="Switch Environment"
        message={`Are you sure you want to switch to ${pending === 'production' ? 'Production' : 'Sandbox'}? This will affect all active API requests for this provider.`}
        confirmLabel={`Switch to ${pending}`}
        confirmVariant={pending === 'production' ? 'danger' : 'primary'}
        onConfirm={handleConfirm}
        onCancel={() => setPending(null)}
        loading={loading}
      />
    </>
  );
}
