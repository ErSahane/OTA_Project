"use client";

import React, { useState, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import FlightCard from './components/FlightCard';
import SortDropdown from './components/SortDropdown';
import Filters from './components/Filters';

export default function SearchResultsPage() {
  const queryClient = useQueryClient();
  const cached = queryClient.getQueryData<any[]>(['flightSearchResults']) || [];

  const [sortKey, setSortKey] = useState('price'); // price, duration, departure
  const [filters, setFilters] = useState({ airline: [] });

  const filtered = useMemo(() => {
    let data = cached;
    if (filters.airline.length) {
      data = data.filter((flight) => filters.airline.includes(flight.airline));
    }
    return data;
  }, [cached, filters]);

  const sorted = useMemo(() => {
    const data = [...filtered];
    switch (sortKey) {
      case 'price':
        data.sort((a, b) => a.price - b.price);
        break;
      case 'duration':
        data.sort((a, b) => a.duration - b.duration);
        break;
      case 'departure':
        data.sort((a, b) => new Date(a.departure) - new Date(b.departure));
        break;
    }
    return data;
  }, [filtered, sortKey]);

  return (
    <div className="flex flex-col lg:flex-row min-h-screen">
      {/* Desktop sidebar */}
      <aside className="hidden lg:block lg:w-64 border-r p-4">
        <Filters filters={filters} setFilters={setFilters} />
      </aside>
      {/* Main content */}
      <main className="flex-1 p-4">
        {/* Mobile filter button */}
        <div className="lg:hidden mb-4">
          <button
            className="px-4 py-2 bg-gray-200 rounded"
            onClick={() => {
              const dlg = document.getElementById('mobile-filters') as HTMLDialogElement;
              dlg?.showModal();
            }}
          >
            Filters
          </button>
          <dialog id="mobile-filters" className="w-full h-full p-4">
            <button className="absolute top-2 right-2" onClick={() => (document.getElementById('mobile-filters') as HTMLDialogElement).close()}>✕</button>
            <Filters filters={filters} setFilters={setFilters} />
          </dialog>
        </div>
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Search Results</h1>
          <SortDropdown sortKey={sortKey} setSortKey={setSortKey} />
        </div>
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
          {sorted.map((flight) => (
            <FlightCard key={flight.id} flight={flight} />
          ))}
        </div>
        {sorted.length === 0 && (
          <p className="text-center text-gray-500 mt-8">No flights match your criteria.</p>
        )}
      </main>
    </div>
  );
}
