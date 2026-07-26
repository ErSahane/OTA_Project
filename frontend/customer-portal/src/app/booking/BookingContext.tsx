"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

export interface PassengerInfo {
  firstName: string;
  lastName: string;
  age: number;
  gender: string;
}

export interface ContactInfo {
  email: string;
  phone: string;
}

export interface BookingData {
  passengers: PassengerInfo[];
  contact: ContactInfo;
  flightId?: string; // optional, assumed to be set from previous step
}

interface BookingContextProps {
  data: BookingData;
  setPassengers: (p: PassengerInfo[]) => void;
  setContact: (c: ContactInfo) => void;
  setFlightId: (id: string) => void;
}

const BookingContext = createContext<BookingContextProps | undefined>(undefined);

export const BookingProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState<BookingData>({ passengers: [], contact: { email: '', phone: '' } });

  const setPassengers = (p: PassengerInfo[]) => setData(prev => ({ ...prev, passengers: p }));
  const setContact = (c: ContactInfo) => setData(prev => ({ ...prev, contact: c }));
  const setFlightId = (id: string) => setData(prev => ({ ...prev, flightId: id }));

  return (
    <BookingContext.Provider value={{ data, setPassengers, setContact, setFlightId }}>
      {children}
    </BookingContext.Provider>
  );
};

export const useBooking = () => {
  const ctx = useContext(BookingContext);
  if (!ctx) throw new Error('useBooking must be used within BookingProvider');
  return ctx;
};
