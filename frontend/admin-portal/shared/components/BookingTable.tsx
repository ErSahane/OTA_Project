"use client";

import React from 'react';
import { ColumnDef, flexRender, getCoreRowModel, useReactTable } from '@tanstack/react-table';
import { Booking } from '@shared/types/booking';
import { format } from 'date-fns';
import clsx from 'clsx';
import Link from 'next/link';

interface Props {
  bookings: Booking[];
  onSort: (field: string) => void;
  sort: { field: string; order: 'asc' | 'desc' };
}

const columns: ColumnDef<Booking>[] = [
  {
    accessorKey: 'id',
    header: 'ID',
    cell: (info) => {
      const id = info.getValue<string>();
      return (
        <Link href={`/booking/${id}`} className="text-indigo-600 hover:underline">
          {id}
        </Link>
      );
    },
  },
  { accessorKey: 'provider', header: 'Provider' },
  { accessorKey: 'airline', header: 'Airline' },
  {
    accessorKey: 'status',
    header: 'Booking Status',
    cell: (info) => {
      const status = info.getValue<string>();
      return (
        <span className={clsx('px-2 py-1 rounded text-xs', {
          'bg-yellow-200 text-yellow-800': status === 'Pending',
          'bg-green-200 text-green-800': status === 'Confirmed',
          'bg-red-200 text-red-800': status === 'Cancelled',
        })}>
          {status}
        </span>
      );
    },
  },
  {
    accessorKey: 'paymentStatus',
    header: 'Payment',
    cell: (info) => {
      const paymentStatus = info.getValue<string>();
      return (
        <span className={clsx('px-2 py-1 rounded text-xs', {
          'bg-yellow-200 text-yellow-800': paymentStatus === 'Pending',
          'bg-green-200 text-green-800': paymentStatus === 'Paid',
          'bg-red-200 text-red-800': paymentStatus === 'Refunded' || paymentStatus === 'Failed',
        })}>
          {paymentStatus}
        </span>
      );
    },
  },
  {
    accessorKey: 'createdAt',
    header: 'Created',
    cell: (info) => format(new Date(info.getValue<string>()), 'Pp'),
  },
];

export default function BookingTable({ bookings, onSort, sort }: Props) {
  const table = useReactTable({
    data: bookings,
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

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  colSpan={header.colSpan}
                  className="px-4 py-2 text-left text-sm font-medium text-gray-700 cursor-pointer"
                  onClick={() => header.column.getCanSort() && onSort(header.column.id)}
                >
                  {flexRender(header.column.columnDef.header, header.getContext())}
                  {header.column.getIsSorted() ? (
                    header.column.getIsSorted() === 'asc' ? ' 🔼' : ' 🔽'
                  ) : null}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="hover:bg-gray-50">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-4 py-2 text-sm text-gray-800">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
