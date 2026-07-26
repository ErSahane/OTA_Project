// frontend/shared/bookingApi.ts

import api from '@shared/api';
import {
  BookingListResponse,
  BookingDetailResponse,
  ActivityLogEntry,
} from '@shared/types/booking';

export interface BookingQueryParams {
  page: number;
  pageSize: number;
  search?: string;
  provider?: string;
  airline?: string;
  status?: string;
  sortField?: string;
  sortOrder?: 'asc' | 'desc';
}

export const fetchBookings = (params: BookingQueryParams) =>
  api.get<BookingListResponse>('/admin/bookings/', { params });

export const fetchBookingDetail = (id: string) =>
  api.get<BookingDetailResponse>(`/admin/bookings/${id}/`);

export const updateAdminNotes = (id: string, notes: string) =>
  api.patch(`/admin/bookings/${id}/notes/`, { notes });

export const fetchActivityLog = (id: string) =>
  api.get<ActivityLogEntry[]>(`/admin/bookings/${id}/activity/`);
