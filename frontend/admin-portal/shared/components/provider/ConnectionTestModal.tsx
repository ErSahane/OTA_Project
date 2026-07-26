"use client";

import { useState } from 'react';
import { CheckCircleIcon, XCircleIcon, ClockIcon, WifiIcon } from '@heroicons/react/24/outline';
import type { ConnectionTestResult } from '@shared/types/provider';
import { testConnection } from '@shared/providerApi';

interface Props {
  providerId: string;
  open: boolean;
  onClose: () => void;
}

export default function ConnectionTestModal({ providerId, open, onClose }: Props) {
  const [result, setResult] = useState<ConnectionTestResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await testConnection(providerId);
      setResult(res.data);
    } catch {
      setError('Failed to reach the test endpoint. Check network or backend configuration.');
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
        {/* Header */}
        <div className="flex items-center gap-3 mb-5">
          <WifiIcon className="h-6 w-6 text-indigo-600" />
          <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Test Connection</h2>
        </div>

        {/* Result */}
        {result && (
          <div className={`rounded-xl p-4 mb-4 ${result.success ? 'bg-emerald-50 dark:bg-emerald-900/20' : 'bg-red-50 dark:bg-red-900/20'}`}>
            <div className="flex items-center gap-2 mb-2">
              {result.success
                ? <CheckCircleIcon className="h-5 w-5 text-emerald-600" />
                : <XCircleIcon className="h-5 w-5 text-red-600" />}
              <span className={`font-semibold ${result.success ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300'}`}>
                {result.success ? 'Connection Successful' : 'Connection Failed'}
              </span>
            </div>
            <div className="space-y-1.5 text-sm">
              {result.httpStatus && (
                <div className="flex justify-between">
                  <span className="text-slate-500">HTTP Status</span>
                  <span className="font-mono font-medium">{result.httpStatus}</span>
                </div>
              )}
              {result.latencyMs !== undefined && (
                <div className="flex justify-between">
                  <span className="text-slate-500">Latency</span>
                  <span className="font-mono font-medium">{result.latencyMs}ms</span>
                </div>
              )}
              {result.authResult && (
                <div className="flex justify-between">
                  <span className="text-slate-500">Auth</span>
                  <span className="font-medium">{result.authResult}</span>
                </div>
              )}
              {result.errorMessage && (
                <div className="mt-2 rounded-lg bg-red-100 dark:bg-red-900/30 px-3 py-2 text-xs text-red-700 dark:text-red-300">
                  {result.errorMessage}
                </div>
              )}
              <div className="flex items-center gap-1 text-xs text-slate-400 mt-2">
                <ClockIcon className="h-3 w-3" />
                <span>{new Date(result.timestamp).toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-xl bg-red-50 dark:bg-red-900/20 p-3 mb-4 text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-3 justify-end">
          <button
            onClick={onClose}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Close
          </button>
          <button
            onClick={handleTest}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:opacity-50"
          >
            {loading ? (
              <>
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Testing…
              </>
            ) : 'Run Test'}
          </button>
        </div>
      </div>
    </div>
  );
}
