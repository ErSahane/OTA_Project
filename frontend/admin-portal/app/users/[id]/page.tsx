"use client"

import React, { useState } from "react"
import { useUser, useUpdateUser } from "@shared/api/usersApi"
import LoadingSkeleton from "@shared/components/admin/LoadingSkeleton"
import UserCard from "@shared/components/admin/UserCard"
import { format } from "date-fns"

export default function UserDetailPage({ params }: { params: { id: string } }) {
  const { id } = params
  const { data: user, isLoading, isError, error } = useUser(id)
  const updateMutation = useUpdateUser()
  const [activeTab, setActiveTab] = useState("profile")

  if (isLoading) {
    return (
      <div className="p-6">
        <LoadingSkeleton rows={3} />
      </div>
    )
  }

  if (isError || !user) {
    return (
      <div className="p-6 text-red-600 dark:text-red-400">
        Error: {error?.message ?? "User not found"}
      </div>
    )
  }

  const handleStatusToggle = () => {
    const newStatus = user.status === "active" ? "inactive" : "active"
    updateMutation.mutate({ id: user.id, data: { status: newStatus } })
  }

  const tabs = [
    { key: "profile", label: "Profile" },
    { key: "roles", label: "Roles" },
    { key: "permissions", label: "Permissions" },
    { key: "sessions", label: "Sessions" },
    { key: "audit", label: "Audit" },
    { key: "security", label: "Security" },
  ]

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4 text-slate-800 dark:text-slate-200">User Detail</h1>
      <UserCard user={user} />
      <div className="flex items-center gap-4 mt-4">
        <button
          onClick={handleStatusToggle}
          className="px-3 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700"
        >
          {user.status === "active" ? "Deactivate" : "Activate"}
        </button>
        <a
          href={`/users/${user.id}/edit`}
          className="px-3 py-1 rounded bg-gray-600 text-white hover:bg-gray-700"
        >
          Edit
        </a>
      </div>

      {/* Tabs */}
      <div className="mt-6 border-b border-slate-200 dark:border-slate-700">
        <nav className="flex space-x-4">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-3 py-2 text-sm font-medium ${activeTab === tab.key ? "border-b-2 border-indigo-600 text-indigo-600" : "text-slate-600 dark:text-slate-300"}`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="mt-4">
        {activeTab === "profile" && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <strong>Name:</strong> {user.name}
            </div>
            <div>
              <strong>Email:</strong> {user.email}
            </div>
            <div>
              <strong>Role ID:</strong> {user.roleId}
            </div>
            <div>
              <strong>Department ID:</strong> {user.departmentId}
            </div>
            <div>
              <strong>Status:</strong> {user.status}
            </div>
            <div>
              <strong>MFA Enabled:</strong> {user.mfaEnabled ? "Yes" : "No"}
            </div>
            <div>
              <strong>Last Login:</strong>{" "}
              {user.lastLogin ? format(new Date(user.lastLogin), "PPpp") : "—"}
            </div>
            <div>
              <strong>Created At:</strong> {format(new Date(user.createdAt), "PPpp")}
            </div>
          </div>
        )}
        {/* Placeholder content for other tabs */}
        {activeTab !== "profile" && (
          <div className="text-sm text-slate-600 dark:text-slate-400">{`Content for ${activeTab} will be implemented later.`}</div>
        )}
      </div>
    </div>
  )
}
