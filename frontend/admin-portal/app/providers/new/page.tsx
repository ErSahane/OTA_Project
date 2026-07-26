"use client"

import { useRouter } from 'next/navigation';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import ProviderForm, { ProviderFormValues } from '@shared/components/provider/ProviderForm';
import { createProvider } from '@shared/providerApi';
import { ArrowPathIcon } from '@heroicons/react/24/outline';

export default function ProviderCreatePage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const createMutation = useMutation((data: ProviderFormValues) => createProvider(data), {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
      router.replace('/providers');
    },
  });

  const handleSubmit = async (values: ProviderFormValues) => {
    try {
      await createMutation.mutateAsync(values);
    } catch (e) {
      // Errors are displayed inside ProviderForm via react-hook-form validation; network errors can be shown via alert.
      alert('Failed to create provider: ' + (e instanceof Error ? e.message : String(e)));
    }
  };

  return (
    <section className="p-6">
      <h1 className="mb-4 text-2xl font-bold text-slate-800 dark:text-slate-100">Create New Provider</h1>
      <ProviderForm onSubmit={handleSubmit} isLoading={createMutation.isLoading} />
      {createMutation.isLoading && (
        <div className="mt-4 flex items-center gap-2 text-indigo-600 dark:text-indigo-400">
          <ArrowPathIcon className="h-5 w-5 animate-spin" />
          <span>Creating provider…</span>
        </div>
      )}
    </section>
  );
}
