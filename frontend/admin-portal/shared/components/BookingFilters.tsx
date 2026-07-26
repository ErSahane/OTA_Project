"use client";

import { useState, ChangeEvent } from 'react';
import clsx from 'clsx';

interface Props {
  onChange: (filters: { provider: string; airline: string; status: string }) => void;
  onSearch: (term: string) => void;
}

const providers = ['ProviderA', 'ProviderB', 'ProviderC']; // TODO: replace with dynamic data
const airlines = ['AirlineX', 'AirlineY', 'AirlineZ'];
const statuses = ['Pending', 'Confirmed', 'Cancelled'];

export default function BookingFilters({ onChange, onSearch }: Props) {
  const [localFilters, setLocalFilters] = useState({ provider: '', airline: '', status: '' });
  const [searchTerm, setSearchTerm] = useState('');

  const handleSelectChange = (e: ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    const updated = { ...localFilters, [name]: value };
    setLocalFilters(updated);
    onChange(updated);
  };

  const handleSearch = () => {
    onSearch(searchTerm);
  };

  return (
    <div className="flex flex-wrap gap-4 items-center mb-4">
      <input
        type="text"
        placeholder="Search…"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="border rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
      />
      <select
        name="provider"
        value={localFilters.provider}
        onChange={handleSelectChange}
        className={clsx('border rounded px-2 py-1', 'focus:outline-none focus:ring-2 focus:ring-indigo-500')}
      >
        <option value="">All Providers</option>
        {providers.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <select
        name="airline"
        value={localFilters.airline}
        onChange={handleSelectChange}
        className={clsx('border rounded px-2 py-1', 'focus:outline-none focus:ring-2 focus:ring-indigo-500')}
      >
        <option value="">All Airlines</option>
        {airlines.map((a) => (
          <option key={a} value={a}>
            {a}
          </option>
        ))}
      </select>
      <select
        name="status"
        value={localFilters.status}
        onChange={handleSelectChange}
        className={clsx('border rounded px-2 py-1', 'focus:outline-none focus:ring-2 focus:ring-indigo-500')}
      >
        <option value="">All Statuses</option>
        {statuses.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
      <button
        onClick={handleSearch}
        className="bg-indigo-600 text-white px-4 py-1 rounded hover:bg-indigo-700 transition"
      >
        Search
      </button>
    </div>
  );
}
