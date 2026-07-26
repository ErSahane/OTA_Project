"use client"

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
// ProviderCard is not used in this page
import { fetchProvider, updateProvider, deleteProvider } from '@shared/providerApi';
import ProviderForm, { ProviderFormValues } from '@shared/components/provider/ProviderForm';
import EnvironmentSwitcher from '@shared/components/provider/EnvironmentSwitcher';
import ConnectionTestModal from '@shared/components/provider/ConnectionTestModal';
import CredentialCard from '@shared/components/provider/CredentialCard';
import AuditTimeline from '@shared/components/provider/AuditTimeline';
// ProviderStats component is not used here
import ProviderHealthBadge from '@shared/components/provider/ProviderHealthBadge';
import ProviderStatusBadge from '@shared/components/provider/ProviderStatusBadge';
import ProviderTypeBadge from '@shared/components/provider/ProviderTypeBadge';
import ConfirmDialog from '@shared/components/provider/ConfirmDialog';
import { format } from 'date-fns';
import type { Provider, ProviderCredential, ProviderHealthMetrics, AuditLogEntry, ProviderEnvironment, UpdateProviderPayload } from '@shared/types/provider';

export default function ProviderDetailPage() {
  const router = useRouter();
  const { id } = useParams() as { id: string };
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<'general' | 'credentials' | 'configuration' | 'health' | 'audit'>('general');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);

  const { data: provider, isLoading, isError, error } = useQuery({
  queryKey: ['provider', id],
  queryFn: () => fetchProvider(id).then(res => res.data),
});
  // Extend provider with optional fields for credentials, healthMetrics, and auditLog
  type ProviderDetail = Provider & {
    credentials?: ProviderCredential[];
    healthMetrics?: ProviderHealthMetrics;
    auditLog?: AuditLogEntry[];
  };
  const providerDetail = provider as ProviderDetail;

  const updateMutation = useMutation((values: ProviderFormValues) => updateProvider(id, values), {
    onSuccess: () => queryClient.invalidateQueries(['provider', id]),
  });

  const deleteMutation = useMutation(() => deleteProvider(id), {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
      router.replace('/providers');
    },
  });

  const handleEnvSwitch = async (env: ProviderEnvironment) => {
    const payload: UpdateProviderPayload = { environment: env };
    await updateMutation.mutateAsync(payload);
  };

  const handleDelete = async () => {
    await deleteMutation.mutateAsync();
    setShowDeleteConfirm(false);
  };

  if (isLoading) return <div className="p-6 text-center text-slate-600 dark:text-slate-400">Loading provider…</div>;
  if (isError) return <div className="p-6 text-red-600 dark:text-red-300">Error loading provider: {(error instanceof Error ? error.message : String(error))}</div>;

  const tabs = [
    { id: 'general', label: 'General' },
    { id: 'credentials', label: 'Credentials' },
    { id: 'configuration', label: 'Configuration' },
    { id: 'health', label: 'Health' },
    { id: 'audit', label: 'Audit Log' },
  ];

  return (
    <section className="p-6">
      {/* Header with actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">{provider.name}</h1>
        <div className="flex items-center gap-3 mt-3 md:mt-0">

          <button
            onClick={() => setShowTestModal(true)}
            className="rounded-lg bg-indigo-600 px-3 py-1 text-sm text-white hover:bg-indigo-700"
          >
            Test Connection
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="rounded-lg bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>

      {/* Badges summary */}
      <div className="flex flex-wrap gap-3 mb-6">
        <ProviderTypeBadge type={providerDetail.type} />
        <ProviderStatusBadge status={providerDetail.status} />
        <ProviderHealthBadge health={providerDetail.health} />
        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
          providerDetail.environment === 'production'
            ? 'bg-indigo-100 text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300'
            : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
        }`}>
          {providerDetail.environment === 'production' ? '🚀 Production' : '🧪 Sandbox'}
        </span>
      </div>

      {/* Tabs */}
      <nav className="mb-6 border-b border-slate-200 dark:border-slate-700">
        <ul className="flex space-x-4">
          {tabs.map((tab) => (
            <li key={tab.id}>
              <button
                onClick={() => setActiveTab(tab.id)}
                className={`rounded-t-lg px-4 py-2 text-sm font-medium ${activeTab === tab.id
                  ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-800 dark:text-slate-100'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300'}
                `}
              >
                {tab.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Tab content */}
      <div className="bg-white p-5 rounded-xl shadow-sm dark:bg-slate-800">
        {activeTab === 'general' && (
          <div className="space-y-6">
            <ProviderForm
              defaultValues={provider}
              onSubmit={(values) => updateMutation.mutateAsync(values)}
              isLoading={updateMutation.isLoading}
            />
            <div className="border-t pt-4">
              <h2 className="text-lg font-semibold mb-2">Metadata</h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Created by {provider.createdBy} on {format(new Date(provider.createdAt), 'PPpp')}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Last updated {format(new Date(provider.updatedAt), 'PPpp')}
              </p>
            </div>
          </div>
        )}
        {activeTab === 'credentials' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {providerDetail.credentials?.map((cred) => (
              <CredentialCard
                key={cred.id}
                credential={cred}
                canRotate={true}
                onRotate={async (cid) => {
                  await fetch(`/admin/providers/${providerDetail.id}/credentials/${cid}/rotate`, { method: 'POST' });
                  queryClient.invalidateQueries(['provider', id]);
                }}
              />
            ))}
          </div>
        )}
        {activeTab === 'configuration' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Endpoint URLs</h2>
            <p className="text-sm"><strong>Sandbox:</strong> {provider.sandboxUrl || '—'}</p>
            <p className="text-sm"><strong>Production:</strong> {provider.productionUrl || '—'}</p>
            <p className="text-sm"><strong>Documentation:</strong> {provider.documentationUrl || '—'}</p>
            <h2 className="text-lg font-semibold mt-4">Connection Settings</h2>
            <p className="text-sm"><strong>Timeout:</strong> {provider.config?.timeout}s</p>
            <p className="text-sm"><strong>Retry Count:</strong> {provider.config?.retryCount}</p>
            <p className="text-sm"><strong>Rate Limit:</strong> {provider.rateLimits?.requestsPerMinute} req/min</p>
          </div>
        )}
        {activeTab === 'health' && (
          <div className="space-y-4">
            <ProviderHealthBadge health={provider.health} size="md" />
            {providerDetail.healthMetrics && (
              <pre className="bg-slate-100 dark:bg-slate-800 p-3 rounded text-sm overflow-x-auto">
                {JSON.stringify(providerDetail.healthMetrics, null, 2)}
              </pre>
            )}
          </div>
        )}
        {activeTab === 'audit' && (
          <AuditTimeline entries={providerDetail.auditLog || []} />
        )}
      </div>

      {/* Modals */}
      <EnvironmentSwitcher
        current={provider.environment}
        onSwitch={handleEnvSwitch}
        disabled={updateMutation.isLoading}
      />
      <ConnectionTestModal providerId={provider.id} open={showTestModal} onClose={() => setShowTestModal(false)} />
      <ConfirmDialog
        open={showDeleteConfirm}
        title="Delete Provider"
        message="Are you sure you want to delete this provider? This action cannot be undone."
        confirmLabel="Delete"
        confirmVariant="danger"
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteConfirm(false)}
        loading={deleteMutation.isLoading}
      />
    </section>
  );
}
