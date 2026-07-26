"use client";

import React from 'react';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import Link from 'next/link';
import { format } from 'date-fns';
import {
  ChevronUpIcon,
  ChevronDownIcon,
  PencilSquareIcon,
  TrashIcon,
  EyeIcon,
} from '@heroicons/react/20/solid';
import type { Provider } from '@shared/types/provider';
import ProviderTypeBadge from './ProviderTypeBadge';
import ProviderStatusBadge from './ProviderStatusBadge';
import ProviderHealthBadge from './ProviderHealthBadge';

interface Props {
  providers: Provider[];
  sort: { field: string; order: 'asc' | 'desc' };
  onSort: (field: string) => void;
  onDelete?: (id: string) => void;
  canEdit?: boolean;
  canDelete?: boolean;
}

export default function ProviderTable({
  providers,
  sort,
  onSort,
  onDelete,
  canEdit = true,
  canDelete = true,
}: Props) {
  const columns: ColumnDef<Provider>[] = [
    {
      accessorKey: 'name',
      header: 'Provider Name',
      cell: (info) => (
        <Link
          href={`/providers/${info.row.original.id}`}
          className="font-medium text-indigo-600 hover:underline dark:text-indigo-400"
        >
          {info.getValue<string>()}
        </Link>
      ),
    },
    {
      accessorKey: 'type',
      header: 'Type',
      cell: (info) => <ProviderTypeBadge type={info.getValue<Provider['type']>()} />,
    },
    {
      accessorKey: 'environment',
      header: 'Environment',
      cell: (info) => {
        const env = info.getValue<Provider['environment']>();
        return (
          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            env === 'production'
              ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200'
              : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
          }`}>
            {env === 'production' ? '🚀 Production' : '🧪 Sandbox'}
          </span>
        );
      },
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: (info) => <ProviderStatusBadge status={info.getValue<Provider['status']>()} />,
    },
    {
      accessorKey: 'lastSync',
      header: 'Last Sync',
      cell: (info) => {
        const val = info.getValue<string | undefined>();
        return val ? <span className="text-xs text-slate-500">{format(new Date(val), 'Pp')}</span> : <span className="text-xs text-slate-400">—</span>;
      },
    },
    {
      accessorKey: 'health',
      header: 'Health',
      cell: (info) => <ProviderHealthBadge health={info.getValue<Provider['health']>()} />,
    },
    {
      accessorKey: 'createdBy',
      header: 'Created By',
      cell: (info) => <span className="text-xs text-slate-600 dark:text-slate-400">{info.getValue<string>()}</span>,
    },
    {
      accessorKey: 'updatedAt',
      header: 'Updated At',
      cell: (info) => (
        <span className="text-xs text-slate-500">
          {format(new Date(info.getValue<string>()), 'PP')}
        </span>
      ),
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: (info) => {
        const id = info.row.original.id;
        return (
          <div className="flex items-center gap-2">
            <Link href={`/providers/${id}`} title="View" className="text-slate-500 hover:text-indigo-600">
              <EyeIcon className="h-4 w-4" />
            </Link>
            {canEdit && (
              <Link href={`/providers/${id}`} title="Edit" className="text-slate-500 hover:text-amber-600">
                <PencilSquareIcon className="h-4 w-4" />
              </Link>
            )}
            {canDelete && onDelete && (
              <button
                onClick={() => onDelete(id)}
                title="Delete"
                className="text-slate-500 hover:text-red-600"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            )}
          </div>
        );
      },
    },
  ];

  const table = useReactTable({
    data: providers,
    columns,
    getCoreRowModel: getCoreRowModel(),
    state: {
      sorting: [{ id: sort.field, desc: sort.order === 'desc' }],
    },
    onSortingChange: (updater) => {
      const newSort = updater instanceof Function ? updater([]) : updater;
      if (newSort.length) onSort(newSort[0].id);
    },
  });

  const sortableColumns = new Set(['name', 'type', 'status', 'environment', 'health', 'updatedAt']);

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
        <thead className="bg-slate-50 dark:bg-slate-800">
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((header) => {
                const isSortable = sortableColumns.has(header.column.id);
                const isSorted = sort.field === header.column.id;
                return (
                  <th
                    key={header.id}
                    colSpan={header.colSpan}
                    onClick={() => isSortable && onSort(header.column.id)}
                    className={`px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 ${isSortable ? 'cursor-pointer select-none hover:text-slate-700 dark:hover:text-slate-200' : ''}`}
                  >
                    <span className="inline-flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {isSortable && isSorted && (
                        sort.order === 'asc'
                          ? <ChevronUpIcon className="h-3 w-3" />
                          : <ChevronDownIcon className="h-3 w-3" />
                      )}
                    </span>
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white dark:bg-slate-900 dark:divide-slate-800">
          {providers.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="py-16 text-center text-slate-400 dark:text-slate-600">
                <div className="flex flex-col items-center gap-2">
                  <span className="text-4xl">🔌</span>
                  <p className="text-sm font-medium">No providers found</p>
                  <p className="text-xs">Adjust your filters or add a new provider.</p>
                </div>
              </td>
            </tr>
          ) : (
            table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3 text-sm text-slate-700 dark:text-slate-300">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
