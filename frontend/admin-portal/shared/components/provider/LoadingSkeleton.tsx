"use client";

interface Props {
  rows?: number;
  cols?: number;
}

function SkeletonCell() {
  return <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />;
}

export function TableLoadingSkeleton({ rows = 8, cols = 9 }: Props) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
      <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
        <thead className="bg-slate-50 dark:bg-slate-800">
          <tr>
            {Array.from({ length: cols }).map((_, i) => (
              <th key={i} className="px-4 py-3">
                <div className="h-3 w-24 bg-slate-300 dark:bg-slate-600 rounded animate-pulse" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800">
          {Array.from({ length: rows }).map((_, rowIdx) => (
            <tr key={rowIdx}>
              {Array.from({ length: cols }).map((_, colIdx) => (
                <td key={colIdx} className="px-4 py-3">
                  <SkeletonCell />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function CardLoadingSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-xl border border-slate-200 dark:border-slate-700 p-5 space-y-3 animate-pulse">
          <div className="h-5 w-1/2 bg-slate-200 dark:bg-slate-700 rounded" />
          <div className="h-3 w-3/4 bg-slate-100 dark:bg-slate-800 rounded" />
          <div className="h-3 w-1/3 bg-slate-100 dark:bg-slate-800 rounded" />
        </div>
      ))}
    </div>
  );
}
