"use client"

import React from "react"
import UserForm from "@shared/components/admin/UserForm"
import { useRouter } from "next/navigation"

export default function CreateUserPage() {
  const router = useRouter()

  const handleSuccess = () => {
    router.push("/users")
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4 text-slate-800 dark:text-slate-200">Create New User</h1>
      <UserForm isCreate={true} defaultValues={{}} />
    </div>
  )
}
