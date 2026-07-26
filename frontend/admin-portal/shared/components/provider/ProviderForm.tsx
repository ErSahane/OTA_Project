"use client";

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import type { Provider, ProviderType, ProviderEnvironment } from '@shared/types/provider';

const PROVIDER_TYPES: ProviderType[] = [
  'flights', 'hotels', 'cars', 'transfers', 'activities', 'insurance', 'visa', 'packages',
];
const ENVIRONMENTS: ProviderEnvironment[] = ['sandbox', 'production'];

const schema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  slug: z.string().min(2, 'Slug must be at least 2 characters').regex(/^[a-z0-9-]+$/, 'Slug must be lowercase alphanumeric with hyphens'),
  description: z.string().optional(),
  type: z.enum(['flights', 'hotels', 'cars', 'transfers', 'activities', 'insurance', 'visa', 'packages'] as [ProviderType, ...ProviderType[]]),
  environment: z.enum(['sandbox', 'production'] as [ProviderEnvironment, ...ProviderEnvironment[]]),
  sandboxUrl: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  productionUrl: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  documentationUrl: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  timeout: z.coerce.number().min(1).max(300),
  retryCount: z.coerce.number().min(0).max(10),
  rateLimitPerMinute: z.coerce.number().min(1),
});

export type ProviderFormValues = z.infer<typeof schema>;

interface Props {
  defaultValues?: Partial<Provider>;
  onSubmit: (values: ProviderFormValues) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

const inputClass =
  'mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100';

const labelClass = 'block text-sm font-medium text-slate-700 dark:text-slate-300';
const errorClass = 'mt-1 text-xs text-red-500';

export default function ProviderForm({ defaultValues, onSubmit, onCancel, isLoading }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProviderFormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: defaultValues?.name ?? '',
      slug: defaultValues?.slug ?? '',
      description: defaultValues?.description ?? '',
      type: defaultValues?.type ?? 'flights',
      environment: defaultValues?.environment ?? 'sandbox',
      sandboxUrl: defaultValues?.sandboxUrl ?? '',
      productionUrl: defaultValues?.productionUrl ?? '',
      documentationUrl: defaultValues?.documentationUrl ?? '',
      timeout: defaultValues?.config?.timeout ?? 30,
      retryCount: defaultValues?.config?.retryCount ?? 3,
      rateLimitPerMinute: defaultValues?.rateLimits?.requestsPerMinute ?? 60,
    },
  });

  const submitting = isSubmitting || isLoading;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
      {/* Basic Info */}
      <section className="rounded-xl border border-slate-200 dark:border-slate-700 p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
          Basic Information
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="name" className={labelClass}>Provider Name *</label>
            <input id="name" {...register('name')} className={inputClass} placeholder="e.g. Amadeus Flights" />
            {errors.name && <p className={errorClass}>{errors.name.message}</p>}
          </div>
          <div>
            <label htmlFor="slug" className={labelClass}>Slug *</label>
            <input id="slug" {...register('slug')} className={inputClass} placeholder="e.g. amadeus-flights" />
            {errors.slug && <p className={errorClass}>{errors.slug.message}</p>}
          </div>
        </div>
        <div>
          <label htmlFor="description" className={labelClass}>Description</label>
          <textarea id="description" {...register('description')} rows={3} className={inputClass} placeholder="Short description of this provider…" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="type" className={labelClass}>Provider Type *</label>
            <select id="type" {...register('type')} className={inputClass}>
              {PROVIDER_TYPES.map((t) => (
                <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
            {errors.type && <p className={errorClass}>{errors.type.message}</p>}
          </div>
          <div>
            <label htmlFor="environment" className={labelClass}>Environment *</label>
            <select id="environment" {...register('environment')} className={inputClass}>
              {ENVIRONMENTS.map((e) => (
                <option key={e} value={e}>{e.charAt(0).toUpperCase() + e.slice(1)}</option>
              ))}
            </select>
            {errors.environment && <p className={errorClass}>{errors.environment.message}</p>}
          </div>
        </div>
      </section>

      {/* URLs */}
      <section className="rounded-xl border border-slate-200 dark:border-slate-700 p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
          Endpoints & Documentation
        </h2>
        <div>
          <label htmlFor="sandboxUrl" className={labelClass}>Sandbox URL</label>
          <input id="sandboxUrl" {...register('sandboxUrl')} className={inputClass} placeholder="https://sandbox.provider.com/api" />
          {errors.sandboxUrl && <p className={errorClass}>{errors.sandboxUrl.message}</p>}
        </div>
        <div>
          <label htmlFor="productionUrl" className={labelClass}>Production URL</label>
          <input id="productionUrl" {...register('productionUrl')} className={inputClass} placeholder="https://api.provider.com/v1" />
          {errors.productionUrl && <p className={errorClass}>{errors.productionUrl.message}</p>}
        </div>
        <div>
          <label htmlFor="documentationUrl" className={labelClass}>Documentation URL</label>
          <input id="documentationUrl" {...register('documentationUrl')} className={inputClass} placeholder="https://docs.provider.com" />
          {errors.documentationUrl && <p className={errorClass}>{errors.documentationUrl.message}</p>}
        </div>
      </section>

      {/* Configuration */}
      <section className="rounded-xl border border-slate-200 dark:border-slate-700 p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
          Connection Settings
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="timeout" className={labelClass}>Timeout (s)</label>
            <input id="timeout" type="number" {...register('timeout')} className={inputClass} min={1} max={300} />
            {errors.timeout && <p className={errorClass}>{errors.timeout.message}</p>}
          </div>
          <div>
            <label htmlFor="retryCount" className={labelClass}>Retry Count</label>
            <input id="retryCount" type="number" {...register('retryCount')} className={inputClass} min={0} max={10} />
            {errors.retryCount && <p className={errorClass}>{errors.retryCount.message}</p>}
          </div>
          <div>
            <label htmlFor="rateLimitPerMinute" className={labelClass}>Rate Limit (req/min)</label>
            <input id="rateLimitPerMinute" type="number" {...register('rateLimitPerMinute')} className={inputClass} min={1} />
            {errors.rateLimitPerMinute && <p className={errorClass}>{errors.rateLimitPerMinute.message}</p>}
          </div>
        </div>
      </section>

      {/* Actions */}
      <div className="flex items-center justify-end gap-3 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? 'Saving…' : 'Save Provider'}
        </button>
      </div>
    </form>
  );
}
