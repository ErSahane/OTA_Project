"use client";

import { useState } from 'react';
import { EyeIcon, EyeSlashIcon, ClipboardDocumentIcon, ArrowPathIcon } from '@heroicons/react/20/solid';
import type { ProviderCredential } from '@shared/types/provider';

interface Props {
  credential: ProviderCredential;
  onRotate?: (id: string) => void;
  canRotate?: boolean;
}

export default function CredentialCard({ credential, onRotate, canRotate = false }: Props) {
  const [revealed, setRevealed] = useState(false);
  const [copied, setCopied] = useState(false);

  const displayValue = revealed ? credential.maskedValue : '••••••••••••';

  const handleCopy = () => {
    navigator.clipboard.writeText(credential.maskedValue).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const LABEL_MAP: Record<string, string> = {
    api_key: 'API Key',
    api_secret: 'API Secret',
    username: 'Username',
    password: 'Password',
    oauth: 'OAuth Token',
    bearer_token: 'Bearer Token',
    jwt: 'JWT',
    certificate: 'Certificate',
  };

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
          {credential.label || LABEL_MAP[credential.type] || credential.type}
        </span>
        <span className="text-xs text-slate-400 dark:text-slate-500">
          {credential.lastRotated ? `Rotated ${new Date(credential.lastRotated).toLocaleDateString()}` : 'Never rotated'}
        </span>
      </div>

      <div className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-900">
        <code className="flex-1 font-mono text-sm tracking-widest text-slate-700 dark:text-slate-300 select-none">
          {displayValue}
        </code>
        <button
          onClick={() => setRevealed((r) => !r)}
          title={revealed ? 'Hide' : 'Reveal'}
          className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
        >
          {revealed ? <EyeSlashIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
        </button>
        <button
          onClick={handleCopy}
          title="Copy"
          className="text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400"
        >
          {copied
            ? <span className="text-xs text-emerald-500 font-medium">Copied!</span>
            : <ClipboardDocumentIcon className="h-4 w-4" />
          }
        </button>
        {canRotate && onRotate && (
          <button
            onClick={() => onRotate(credential.id)}
            title="Rotate credential"
            className="text-slate-400 hover:text-amber-600 dark:hover:text-amber-400"
          >
            <ArrowPathIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
