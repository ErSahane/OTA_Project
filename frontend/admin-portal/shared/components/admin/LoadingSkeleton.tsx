// LoadingSkeleton component – shows placeholder rows for tables.
"use client"

import React from "react"

export default function LoadingSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <tbody className="divide-y divide-slate-100 bg-white dark:bg-slate-900 dark:divide-slate-800">
      {Array.from({ length: rows }).map((_, i) => (
        <tr key={i} className="animate-pulse">
          <td className="px-4 py-3">
            <div className="h-4 w-3/4 bg-slate-300 dark:bg-slate-700 rounded" />
          </td>
          <td className="px-4 py-3">
            <div className="h-4 w-1/2 bg-slate-300 dark:bg-slate-700 rounded" />
          </td>
          <td className="px-4 py-3">
            <div className="h-4 w-1/3 bg-slate-300 dark:bg-slate-700 rounded" />
          </td>
          <td className="px-4 py-3">
            <div className="h-4 w-1/4 bg-slate-300 dark:bg-slate-700 rounded" />
          </td>
          <td className="px-4 py-3">
            <div className="h-4 w-1/5 bg-slate-300 dark:bg-slate-700 rounded" />
          </td>
          <td className="px-4 py-3">
            <div className="h-4 w-8 bg-slate-300 dark:bg-slate-700 rounded" />
          </td>
        </tr>
      ))}
    </tbody>
  )
}
