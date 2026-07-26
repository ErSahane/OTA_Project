"use client";

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { useRouter } from 'next/navigation';

interface Booking {
  id: string;
  pnr: string;
  flight: string;
  status: string;
  paid_amount: number;
  payment_method: string;
  created_at: string;
}

export default function MyTripsPage() {
  const router = useRouter();
  const { data, isLoading, isError, error } = useQuery<Booking[]>(
    ['myTrips'],
    async () => {
      const res = await api.get('/api/bookings/');
      return res.data;
    },
    { staleTime: 5 * 60 * 1000 }
  );

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }
  if (isError) {
    return <div className="text-red-600">Error loading trips: {(error as any).message}</div>;
  }
  if (!data || data.length === 0) {
    return <div className="text-center text-gray-600 mt-8">You have no trips yet.</div>;
  }

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">My Trips</h1>
      <ul className="space-y-4">
        {data.map((booking) => (
          <li
            key={booking.id}
            className="border rounded p-4 hover:shadow cursor-pointer"
            onClick={() => router.push(`/my-trips/${booking.id}`)}
          >
            <div className="flex justify-between items-center">
              <div>
                <p className="font-medium">PNR: {booking.pnr}</p>
                <p className="text-sm text-gray-500">Flight: {booking.flight}</p>
              </div>
              <div className="text-right">
                <p className="font-semibold">${booking.paid_amount}</p>
                <p className="text-sm text-gray-500">{booking.status}</p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
