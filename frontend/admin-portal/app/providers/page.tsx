"use client";

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import ProviderTable from '@shared/components/provider/ProviderTable';
import ProviderFilters from '@shared/components/provider/ProviderFilters';
import SearchBar from '@shared/components/provider/SearchBar';
import { TableLoadingSkeleton } from '@shared/components/provider/LoadingSkeleton';
import { fetchProviders, fetchProviderStats, deleteProvider } from '@shared/providerApi';
import type { ProviderListResponse, ProviderQueryParams, ProviderStats } from '@shared/types/provider';

export default function ProvidersPage() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({ status: '', type: '' } as const);
  const [sortField, setSortField] = useState('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const queryParams: ProviderQueryParams = {
    page,
    pageSize,
    search: search || undefined,
    status: filters.status || undefined,
    type: filters.type || undefined,
    sortField,
    sortOrder,
  };

  const { data, isLoading, isError, error } = useQuery<ProviderListResponse>(
    ['providers', queryParams],
    () => fetchProviders(queryParams).then((res) => res.data),
    { keepPreviousData: true },
  );

  const { data: statsData } = useQuery<ProviderStats>('providerStats', () =>
    fetchProviderStats().then((res) => res.data),
  );

  const deleteMutation = useMutation((id: string) => deleteProvider(id), {
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['providers'] }),
  });

  const handleDelete = (id: string) => {
    if (confirm('Delete this provider? This action cannot be undone.')) {
      deleteMutation.mutate(id);
    }
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
    setPage(1);
  };

  // Pagination controls (simple)
  const totalPages = data ? Math.ceil(data.count / pageSize) : 0;

  const goPrev = () => setPage((p) => Math.max(p - 1, 1));
  const goNext = () => setPage((p) => Math.min(p + 1, totalPages));

  // Sync URL query params for deep linking (optional, omitted for brevity)

  return (
    <section className="p-6">
      <h1 className="mb-4 text-2xl font-bold text-slate-800 dark:text-slate-100">Providers</h1>

      {/* Stats */}
      {statsData && (
        <div className="mb-4">
          {/* Simple stats summary */}
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Total: {statsData.total} • Active: {statsData.active} • Healthy: {statsData.healthy}
          </p>
        </div>
      )}

      {/* Controls */}
      <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <SearchBar onSearch={(term) => { setSearch(term); setPage(1); }} />
        <ProviderFilters filters={filters} onChange={(f) => { setFilters(f); setPage(1); }} />
        <button
          onClick={() => router.push('/providers/new')}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-400"
        >
          + New Provider
        </button>
      </div>

      {/* Table or skeleton */}
      {isLoading ? (
        <TableLoadingSkeleton rows={8} cols={9} />
      ) : isError ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
          <p>Failed to load providers: {(error instanceof Error ? error.message : String(error)) || 'Unknown error'}</p>
          <button onClick={() => router.refresh()} className="mt-2 underline">Retry</button>
        </div>
      ) : (
        <ProviderTable
          providers={data?.results ?? []}
          sort={{ field: sortField, order: sortOrder }}
          onSort={handleSort}
          onDelete={handleDelete}
          canEdit={true}
          canDelete={true}
        />
      )}

      {/* Pagination */}
      {data && (
        <div className="mt-4 flex items-center justify-center gap-4 text-sm text-slate-600 dark:text-slate-400">
          <button
            onClick={goPrev}
            disabled={page === 1}
            className="rounded border border-slate-300 bg-white px-2 py-1 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-600 dark:bg-slate-800 dark:hover:bg-slate-700"
          >
            ← Prev
          </button>
          <span>Page {page} of {totalPages}</span>
          <button
            onClick={goNext}
            disabled={page === totalPages}
            className="rounded border border-slate-300 bg-white px-2 py-1 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-600 dark:bg-slate-800 dark:hover:bg-slate-700"
          >
            Next →
          </button>
        </div>
      )}
    </section>
  );
}
