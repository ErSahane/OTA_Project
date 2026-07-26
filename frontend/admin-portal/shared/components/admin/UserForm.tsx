"use client"

import React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { userSchema, type UserFormValues } from "@shared/schemas/user"
import { useCreateUser, useUpdateUser } from "@shared/api/usersApi"
import { useRouter } from "next/navigation"

interface Props {
  /** When editing, provide the existing user data. */
  defaultValues?: Partial<UserFormValues> & { id?: string }
  /** Set true to render a submit button labeled "Create"; false renders "Update". */
  isCreate?: boolean
}

export default function UserForm({ defaultValues, isCreate = true }: Props) {
  const router = useRouter()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserFormValues>({
    resolver: zodResolver(userSchema),
    defaultValues,
  })

  const createMutation = useCreateUser()
  const updateMutation = useUpdateUser()

  const onSubmit = async (data: UserFormValues) => {
    if (isCreate) {
      await createMutation.mutateAsync(data)
      router.push("/users")
    } else if (defaultValues?.id) {
      await updateMutation.mutateAsync({ id: defaultValues.id, data })
      router.push(`/users/${defaultValues.id}`)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-xl">
      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Name
        </label>
        <input
          {...register("name")}
          className="mt-1 block w-full rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 p-2 text-sm text-slate-900 dark:text-slate-100"
        />
        {errors.name && <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Email
        </label>
        <input
          type="email"
          {...register("email")}
          className="mt-1 block w-full rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 p-2 text-sm text-slate-900 dark:text-slate-100"
        />
        {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Role</label>
        <input
          {...register("roleId")}
          className="mt-1 block w-full rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 p-2 text-sm text-slate-900 dark:text-slate-100"
          placeholder="role ID"
        />
        {errors.roleId && <p className="mt-1 text-xs text-red-600">{errors.roleId.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Department</label>
        <input
          {...register("departmentId")}
          className="mt-1 block w-full rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 p-2 text-sm text-slate-900 dark:text-slate-100"
          placeholder="department ID"
        />
        {errors.departmentId && <p className="mt-1 text-xs text-red-600">{errors.departmentId.message}</p>}
      </div>

      <div className="flex items-center space-x-4">
        <label className="inline-flex items-center">
          <input type="checkbox" {...register("mfaEnabled")} className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
          <span className="ml-2 text-sm text-slate-700 dark:text-slate-300">MFA Enabled</span>
        </label>
      </div>

      <div>
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {isCreate ? "Create User" : "Update User"}
        </button>
      </div>
    </form>
  )
}
