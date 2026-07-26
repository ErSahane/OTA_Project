// frontend/shared/types/booking.ts

export interface Passenger {
  id: string;
  name: string;
  age: number;
  ticketNumber?: string;
}

export interface FareComponent {
  description: string;
  amount: number;
}

export interface Payment {
  id: string;
  amount: number;
  status: 'Pending' | 'Completed' | 'Failed';
  method: string;
  timestamp: string; // ISO string
}

export interface ActivityLogEntry {
  id: string;
  user: string;
  action: string;
  timestamp: string;
}

export interface Booking {
  id: string;
  provider: string;
  airline: string;
  status: 'Pending' | 'Confirmed' | 'Cancelled';
  paymentStatus: 'Pending' | 'Paid' | 'Refunded';
  createdAt: string; // ISO
  updatedAt: string;
  passengers: Passenger[];
  fareComponents: FareComponent[];
  totalAmount: number;
  notes?: string;
}

export interface BookingListResponse {
  results: Booking[];
  count: number;
  next?: string;
  previous?: string;
}

export type BookingDetailResponse = Booking;
