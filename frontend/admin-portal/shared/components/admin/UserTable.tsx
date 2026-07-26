/*
  UserTable component – renders a TanStack Table for users with sorting, pagination UI.
  Reuses shared components for loading skeleton, avatar, status badge, etc.
*/
"use client";

import React from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import Link from "next/link";
import { format } from "date-fns";
import { User } from "@shared/types/user";
import Avatar from "./Avatar";
import StatusBadge from "./StatusBadge";
import MFABadge from "./MFABadge";

interface Props {
  users: User[];
  sort: { field: string; order: "asc" | "desc" };
  onSort: (field: string) => void;
  onDelete?: (id: string) => void;
  canEdit?: boolean;
  canDelete?: boolean;
  /** IDs of rows currently selected */
  selectedIds: string[];
  /** Callback when selection changes */
  onSelectionChange: (ids: string[]) => void;
}

export default function UserTable({
  users,
  sort,
  onSort,
  onDelete,
  canEdit = true,
  canDelete = true,
}: Props) {
  const toggleRow = (id: string) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((sid) => sid !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };
  const toggleAll = () => {
    if (selectedIds.length === users.length && users.length > 0) {
      onSelectionChange([]);
    } else {
      onSelectionChange(users.map((u) => u.id));
    }
  };
  const columns: ColumnDef<User>[] = [
    {
      id: "select",
      header: () => (
        <input
          type="checkbox"
          checked={selectedIds.length === users.length && users.length > 0}
          onChange={toggleAll}
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
      ),
      cell: (info) => (
        <input
          type="checkbox"
          checked={selectedIds.includes(info.row.original.id)}
          onChange={() => toggleRow(info.row.original.id)}
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
      ),
    },
    {
      accessorKey: "avatar",
      header: "Avatar",
      cell: (info) => {
        const { name, avatarUrl } = info.row.original;
        return <Avatar name={name} src={avatarUrl} size="sm" />;
      },
    },
    {
      accessorKey: "name",
      header: "Name",
      cell: (info) => (
        <Link
          href={`/users/${info.row.original.id}`}
          className="font-medium text-indigo-600 hover:underline dark:text-indigo-400"
        >
          {info.getValue<string>()}
        </Link>
      ),
    },
    { accessorKey: "email", header: "Email" },
    {
      accessorKey: "role",
      header: "Role",
      cell: (info) => <span className="text-sm">{info.getValue<string>()}</span>,
    },
    { accessorKey: "department", header: "Department" },
    {
      accessorKey: "status",
      header: "Status",
      cell: (info) => <StatusBadge status={info.getValue<string>()} />,
    },
    {
      accessorKey: "mfaEnabled",
      header: "MFA",
      cell: (info) => <MFABadge enabled={info.getValue<boolean>()} />,
    },
    {
      accessorKey: "lastLogin",
      header: "Last Login",
      cell: (info) => {
        const val = info.getValue<string | null>();
        return val ? (
          <span className="text-xs text-slate-500">
            {format(new Date(val), "Pp")}
          </span>
        ) : (
          <span className="text-xs text-slate-400">—</span>
        );
      },
    },
    {
      accessorKey: "createdAt",
      header: "Created",
      cell: (info) => (
        <span className="text-xs text-slate-500">
          {format(new Date(info.getValue<string>()), "PP")}
        </span>
      ),
    },
    {
      id: "actions",
      header: "Actions",
      cell: (info) => {
        const id = info.row.original.id;
        return (
          <div className="flex items-center gap-2 text-sm">
            <Link
              href={`/users/${id}`}
              title="View"
              className="text-slate-500 hover:text-indigo-600"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </Link>
            {canEdit && (
              <Link
                href={`/users/${id}/edit`}
                title="Edit"
                className="text-slate-500 hover:text-amber-600"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5h2M12 7v12m0-12h2a2 2 0 012 2v8a2 2 0 01-2 2h-2"
                  />
                </svg>
              </Link>
            )}
            {canDelete && onDelete && (
              <button
                onClick={() => onDelete(id)}
                title="Delete"
                className="text-slate-500 hover:text-red-600"
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>
        );
      },
    },
  ];

  const table = useReactTable({
    data: users,
    columns,
    getCoreRowModel: getCoreRowModel(),
    state: {
      sorting: [{ id: sort.field, desc: sort.order === "desc" }],
    },
    onSortingChange: (updater) => {
      const newSort = updater instanceof Function ? updater([]) : updater;
      if (newSort.length) onSort(newSort[0].id);
    },
  });

  const sortableColumns = new Set([
    "name",
    "email",
    "role",
    "department",
    "status",
    "lastLogin",
    "createdAt",
  ]);

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
                    className={`px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 ${
                      isSortable
                        ? "cursor-pointer select-none hover:text-slate-700 dark:hover:text-slate-200"
                        : ""
                    }`}
                  >
                    <span className="inline-flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {isSortable && isSorted && (
                        sort.order === "asc" ? (
                          <svg
                            className="h-3 w-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 15l7-7 7 7"
                            />
                          </svg>
                        ) : (
                          <svg
                            className="h-3 w-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 9l-7 7-7-7"
                            />
                          </svg>
                        )
                      )}
                    </span>
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white dark:bg-slate-900 dark:divide-slate-800">
          {users.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="py-16 text-center text-slate-400 dark:text-slate-600">
                <div className="flex flex-col items-center gap-2">
                  <span className="text-4xl">👤</span>
                  <p className="text-sm font-medium">No users found</p>
                  <p className="text-xs">Adjust filters or add a new user.</p>
                </div>
              </td>
            </tr>
          ) : (
            table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
              >
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    className="px-4 py-3 text-sm text-slate-700 dark:text-slate-300"
                  >
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
