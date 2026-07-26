"use client";

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchBookings, BookingQueryParams } from '@shared/bookingApi';
import BookingTable from '@shared/components/BookingTable';
import BookingFilters from '@shared/components/BookingFilters';
import PaginationControls from '@shared/components/PaginationControls';
import { ProtectedRoute } from '@shared/auth/ProtectedRoute';
import { UserRole } from '@shared/types';

const PAGE_SIZE = 20;

interface Filters {
  provider: string;
  airline: string;
  status: string;
}

export default function BookingListPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<Filters>({ provider: '', airline: '', status: '' });
  const [sort, setSort] = useState<{ field: string; order: 'asc' | 'desc' }>({ field: 'createdAt', order: 'desc' });

  const queryParams: BookingQueryParams = {
    page,
    pageSize: PAGE_SIZE,
    search,
    provider: filters.provider || undefined,
    airline: filters.airline || undefined,
    status: filters.status || undefined,
    sortField: sort.field,
    sortOrder: sort.order,
  };

  const { data, isLoading, error } = useQuery({
    queryKey: ['bookings', queryParams],
    queryFn: () => fetchBookings(queryParams),
  });

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters);
    setPage(1);
  };

  const handleSearch = (term: string) => {
    setSearch(term);
    setPage(1);
  };

  const handleSort = (field: string) => {
    setSort((prev) => ({
      field,
      order: prev.field === field && prev.order === 'desc' ? 'asc' : 'desc',
    }));
  };

  if (isLoading) return <p className="p-4">Loading bookings…</p>;
  if (error) return <p className="p-4 text-red-600">Failed to load bookings.</p>;

  const bookings = data?.data?.results ?? [];
  const total = data?.data?.count ?? 0;

  return (
    <ProtectedRoute requiredRoles={['SuperAdmin', 'Operations', 'Finance', 'Support'] as UserRole[]}>
      <div className="p-6 space-y-4">
        <h1 className="text-2xl font-bold">Booking Management</h1>
        <BookingFilters onChange={handleFilterChange} onSearch={handleSearch} />
        <BookingTable bookings={bookings} onSort={handleSort} sort={sort} />
        <PaginationControls
          currentPage={page}
          pageSize={PAGE_SIZE}
          totalCount={total}
          onPageChange={setPage}
        />
      </div>
    </ProtectedRoute>
  );
}
