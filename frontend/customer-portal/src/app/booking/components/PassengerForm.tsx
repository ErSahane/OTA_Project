"use client";

import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import * as yup from 'yup';
import { yupResolver } from '@hookform/resolvers/yup';
import { useBooking } from '../BookingContext';

interface FormValues {
  firstName: string;
  lastName: string;
  age: number;
  gender: string;
}

const schema = yup.object({
  firstName: yup.string().required('First name required'),
  lastName: yup.string().required('Last name required'),
  age: yup.number().min(0, 'Invalid age').required('Age required'),
  gender: yup.string().required('Gender required'),
});

export default function PassengerForm({ onNext }: { onNext: () => void }) {
  const { setPassengers } = useBooking();
  const { control, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: yupResolver(schema),
    defaultValues: { firstName: '', lastName: '', age: 0, gender: '' },
  });

  const onSubmit = (data: FormValues) => {
    setPassengers([data]);
    onNext();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-2">Passenger Details</h2>
      <Controller
        name="firstName"
        control={control}
        render={({ field }) => (
          <input {...field} placeholder="First Name" className="w-full border p-2" />
        )}
      />
      {errors.firstName && <p className="text-red-600 text-sm">{errors.firstName.message}</p>}
      <Controller
        name="lastName"
        control={control}
        render={({ field }) => (
          <input {...field} placeholder="Last Name" className="w-full border p-2" />
        )}
      />
      {errors.lastName && <p className="text-red-600 text-sm">{errors.lastName.message}</p>}
      <Controller
        name="age"
        control={control}
        render={({ field }) => (
          <input type="number" {...field} placeholder="Age" className="w-full border p-2" />
        )}
      />
      {errors.age && <p className="text-red-600 text-sm">{errors.age.message}</p>}
      <Controller
        name="gender"
        control={control}
        render={({ field }) => (
          <select {...field} className="w-full border p-2">
            <option value="">Select Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        )}
      />
      {errors.gender && <p className="text-red-600 text-sm">{errors.gender.message}</p>}
      <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition">
        Continue
      </button>
    </form>
  );
}
