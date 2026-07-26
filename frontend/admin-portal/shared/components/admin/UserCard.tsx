"use client"

import React from "react"
import Avatar from "./Avatar"
import StatusBadge from "./StatusBadge"
import Link from "next/link"
import { User } from "@shared/types/user"

interface Props {
  user: User
}

export default function UserCard({ user }: Props) {
  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm p-4 flex items-center space-x-4">
      <Avatar name={user.name} src={user.avatarUrl} size="md" />
      <div className="flex-1">
        <Link
          href={`/users/${user.id}`}
          className="block text-lg font-medium text-indigo-600 hover:underline dark:text-indigo-400"
        >
          {user.name}
        </Link>
        <p className="text-sm text-slate-600 dark:text-slate-300">{user.email}</p>
        <p className="text-sm text-slate-600 dark:text-slate-300">{user.roleId}</p>
      </div>
      <StatusBadge status={user.status} />
    </div>
  )
}
