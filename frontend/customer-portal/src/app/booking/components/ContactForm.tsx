"use client";

import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { useBooking } from '../BookingContext';

interface FormValues {
  email: string;
  phone: string;
}

const schema = yup.object({
  email: yup.string().email('Invalid email').required('Email required'),
  phone: yup.string().required('Phone required'),
});

export default function ContactForm({ onNext }: { onNext: () => void }) {
  const { setContact } = useBooking();
  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: yupResolver(schema),
    defaultValues: { email: '', phone: '' },
  });

  const onSubmit = (data: FormValues) => {
    setContact(data);
    onNext();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-2">Contact Details</h2>
      <Controller
        name="email"
        control={control}
        render={({ field }) => (
          <input {...field} placeholder="Email" className="w-full border p-2" />
        )}
      />
      {errors.email && <p className="text-red-600 text-sm">{errors.email.message}</p>}
      <Controller
        name="phone"
        control={control}
        render={({ field }) => (
          <input {...field} placeholder="Phone" className="w-full border p-2" />
        )}
      />
      {errors.phone && <p className="text-red-600 text-sm">{errors.phone.message}</p>}
      <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition">
        Continue
      </button>
    </form>
  );
}
