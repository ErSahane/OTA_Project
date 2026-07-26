// SearchBar component – controlled input with clear button.
"use client";

import React from "react";
import { XMarkIcon } from "@heroicons/react/24/outline";

interface Props {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export default function SearchBar({ value, onChange, placeholder }: Props) {
  return (
    <div className="relative flex items-center w-full max-w-sm">
      <input
        type="text"
        className="w-full rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 py-1 pl-3 pr-8 text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        placeholder={placeholder ?? "Search..."}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {value && (
        <button
          type="button"
          className="absolute right-2 text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
          onClick={() => onChange("")}
        >
          <XMarkIcon className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
