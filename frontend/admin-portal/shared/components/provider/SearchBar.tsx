"use client";

import { useState, useEffect, ChangeEvent } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/20/solid';

interface Props {
  placeholder?: string;
  debounceMs?: number;
  onSearch: (term: string) => void;
}

export default function SearchBar({ placeholder = 'Search providers…', debounceMs = 300, onSearch }: Props) {
  const [value, setValue] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => onSearch(value.trim()), debounceMs);
    return () => clearTimeout(timer);
  }, [value, debounceMs, onSearch]);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => setValue(e.target.value);
  const handleClear = () => setValue('');

  return (
    <div className="relative flex items-center">
      <MagnifyingGlassIcon className="pointer-events-none absolute left-3 h-4 w-4 text-slate-400" />
      <input
        id="provider-search"
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-8 text-sm text-slate-800 placeholder-slate-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-300 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 dark:placeholder-slate-500"
      />
      {value && (
        <button
          onClick={handleClear}
          aria-label="Clear search"
          className="absolute right-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
        >
          <XMarkIcon className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
