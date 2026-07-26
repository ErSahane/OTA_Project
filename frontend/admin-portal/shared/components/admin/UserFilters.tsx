// UserFilters component – provides search and filter controls for the Users list.
"use client"

import React, { useState, useEffect } from "react"
import { debounce } from "lodash"
import SearchBar from "./SearchBar"

interface FilterOption {
  value: string;
  label: string;
}

interface Props {
  search: string;
  onSearchChange: (value: string) => void;
  status: string;
  onStatusChange: (value: string) => void;
  role: string;
  onRoleChange: (value: string) => void;
  department: string;
  onDepartmentChange: (value: string) => void;
}

const statusOptions: FilterOption[] = [
  { value: "", label: "All Statuses" },
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
  { value: "pending", label: "Pending" },
];

// Placeholder options – in a real app these would be fetched from the API.
const roleOptions: FilterOption[] = [
  { value: "", label: "All Roles" },
  { value: "admin", label: "Admin" },
  { value: "manager", label: "Manager" },
  { value: "user", label: "User" },
];

const departmentOptions: FilterOption[] = [
  { value: "", label: "All Departments" },
  { value: "sales", label: "Sales" },
  { value: "engineering", label: "Engineering" },
  { value: "support", label: "Support" },
];

export default function UserFilters({
  search,
  onSearchChange,
  status,
  onStatusChange,
  role,
  onRoleChange,
  department,
  onDepartmentChange,
}: Props) {
  const [localSearch, setLocalSearch] = useState(search)

  const debounced = debounce((value: string) => {
    onSearchChange(value)
  }, 300)

  useEffect(() => {
    debounced(localSearch)
    return () => {
      debounced.cancel()
    }
  }, [localSearch])

  return (
    <div className="flex flex-col md:flex-row gap-4 p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
      <SearchBar value={localSearch} onChange={setLocalSearch} placeholder="Search users..." />
      <div className="flex flex-col">
        <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Status</label>
        <select
          className="rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm p-1"
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
        >
          {statusOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col">
        <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Role</label>
        <select
          className="rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm p-1"
          value={role}
          onChange={(e) => onRoleChange(e.target.value)}
        >
          {roleOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col">
        <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">Department</label>
        <select
          className="rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm p-1"
          value={department}
          onChange={(e) => onDepartmentChange(e.target.value)}
        >
          {departmentOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
