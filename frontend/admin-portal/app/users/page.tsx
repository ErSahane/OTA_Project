"use client"

import React, { useState } from "react"
import { useUsers, useDeleteUser, useUpdateUser } from "@shared/api/usersApi"
import UserTable from "@shared/components/admin/UserTable"
import UserFilters from "@shared/components/admin/UserFilters"
import LoadingSkeleton from "@shared/components/admin/LoadingSkeleton"
import PaginationControls from "@shared/components/PaginationControls"

export default function UsersPage() {
  // Table state
  const [page, setPage] = useState(1)
  const pageSize = 20
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState("")
  const [role, setRole] = useState("")
  const [department, setDepartment] = useState("")
  const [sort, setSort] = useState<{ field: string; order: "asc" | "desc" }>({
    field: "name",
    order: "asc",
  })

  // Fetch users – note that API mock currently only supports page, pageSize, search.
  // For status/role/department filters we can apply client‑side filtering for now.
  const { data, isLoading, isError, error } = useUsers(page, pageSize, search)

  const filtered = React.useMemo(() => {
    if (!data) return []
    return data.data.filter((u) => {
      const matchesStatus = status ? u.status === status : true
      const matchesRole = role ? u.roleId === role : true
      const matchesDept = department ? u.departmentId === department : true
      return matchesStatus && matchesRole && matchesDept
    })
  }, [data, status, role, department])

  const deleteMutation = useDeleteUser()

  const handleDelete = (id: string) => {
    if (confirm("Delete this user?")) {
      deleteMutation.mutate(id)
    }
  }

  const handleSort = (field: string) => {
    setSort((prev) => {
      if (prev.field === field) {
        return { field, order: prev.order === "asc" ? "desc" : "asc" }
      }
      return { field, order: "asc" }
    })
  }

  if (isLoading) {
    return (
      <div className="p-4">
        <LoadingSkeleton rows={5} />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="p-4 text-red-600 dark:text-red-400">Error: {error?.message ?? "Failed to load users"}</div>
    )
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4 text-slate-800 dark:text-slate-200">Users</h1>
      <UserFilters
        search={search}
        onSearchChange={setSearch}
        status={status}
        onStatusChange={setStatus}
        role={role}
        onRoleChange={setRole}
        department={department}
        onDepartmentChange={setDepartment}
      />
      <UserTable
        users={filtered}
        sort={sort}
        onSort={handleSort}
        onDelete={handleDelete}
        canEdit={true}
        canDelete={true}
      />
      <PaginationControls
        currentPage={page}
        pageSize={pageSize}
        totalCount={data?.total ?? 0}
        onPageChange={setPage}
      />
    </div>
  )
}
