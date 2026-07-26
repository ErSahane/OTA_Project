"use client";

import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import { useState } from 'react';

// Simple placeholder autocomplete using a static list
const airportOptions = [
  { code: 'JFK', name: 'John F. Kennedy International Airport' },
  { code: 'LAX', name: 'Los Angeles International Airport' },
  { code: 'ORD', name: 'Chicago O\'Hare International Airport' },
  { code: 'DXB', name: 'Dubai International Airport' },
];

const schema = yup.object({
  tripType: yup.string().required(),
  origin: yup.string().required('Select origin'),
  destination: yup.string().required('Select destination'),
  departureDate: yup.date().required('Select departure date'),
  returnDate: yup
    .date()
    .when('tripType', {
      is: 'round',
      then: yup.date().required('Select return date'),
      otherwise: yup.date().nullable(),
    })
    .min(yup.ref('departureDate'), 'Return must be after departure'),
  passengers: yup
    .number()
    .required()
    .min(1, 'At least one passenger')
    .max(9, 'Maximum 9 passengers'),
  cabinClass: yup.string().required(),
});

type FormValues = yup.InferType<typeof schema>;

export default function FlightSearchPage() {
  const [errorMessage, setErrorMessage] = useState('');

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: yupResolver(schema),
    defaultValues: {
      tripType: 'oneway',
      origin: '',
      destination: '',
      departureDate: '',
      returnDate: null,
      passengers: 1,
      cabinClass: 'economy',
    },
  });

import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';

// Inside component
const router = useRouter();
const queryClient = useQueryClient();

const mutation = useMutation(
  (data: FormValues) => api.post('/api/flight-search/search/', data),
  {
    onSuccess: (res) => {
      // Store results in React Query cache
      queryClient.setQueryData(['flightSearchResults'], res.data);
      // Navigate to results page
      router.push('/search/results');
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      setErrorMessage(error.response?.data?.detail || 'Search failed');
    },
  }
);


  const onSubmit = (data: FormValues) => {
    setErrorMessage('');
    mutation.mutate(data);
  };

  // eslint-disable-next-line react-hooks/incompatible-library
const tripType = watch('tripType');

  return (
    <section className="max-w-3xl mx-auto p-4">
      <h1 className="text-2xl font-semibold mb-4">Flight Search</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Trip type selector */}
        <div className="flex space-x-4">
          <label className="inline-flex items-center">
            <input
              type="radio"
              value="oneway"
              {...control.register('tripType')}
              defaultChecked
            />
            <span className="ml-2">One‑Way</span>
          </label>
          <label className="inline-flex items-center">
            <input type="radio" value="round" {...control.register('tripType')} />
            <span className="ml-2">Round‑Trip</span>
          </label>
          <label className="inline-flex items-center">
            <input type="radio" value="multi" {...control.register('tripType')} />
            <span className="ml-2">Multi‑City</span>
          </label>
        </div>

        {/* Origin autocomplete */}
        <Controller
          name="origin"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full border rounded p-2"
              aria-label="Origin airport"
            >
              <option value="">Select origin</option>
              {airportOptions.map((a) => (
                <option key={a.code} value={a.code}>
                  {a.code} – {a.name}
                </option>
              ))}
            </select>
          )}
        />
        {errors.origin && (
          <p className="text-red-600 text-sm">{errors.origin.message}</p>
        )}

        {/* Destination autocomplete */}
        <Controller
          name="destination"
          control={control}
          render={({ field }) => (
            <select
              {...field}
              className="w-full border rounded p-2"
              aria-label="Destination airport"
            >
              <option value="">Select destination</option>
              {airportOptions.map((a) => (
                <option key={a.code} value={a.code}>
                  {a.code} – {a.name}
                </option>
              ))}
            </select>
          )}
        />
        {errors.destination && (
          <p className="text-red-600 text-sm">{errors.destination.message}</p>
        )}

        {/* Departure date */}
        <Controller
          name="departureDate"
          control={control}
          render={({ field }) => (
            <input
              type="date"
              {...field}
              className="w-full border rounded p-2"
              aria-label="Departure date"
            />
          )}
        />
        {errors.departureDate && (
          <p className="text-red-600 text-sm">{errors.departureDate.message}</p>
        )}

        {/* Return date – only for round‑trip */}
        {tripType === 'round' && (
          <Controller
            name="returnDate"
            control={control}
            render={({ field }) => (
              <input
                type="date"
                {...field}
                className="w-full border rounded p-2"
                aria-label="Return date"
              />
            )}
          />
        )}
        {errors.returnDate && (
          <p className="text-red-600 text-sm">{errors.returnDate.message}</p>
        )}

        {/* Passengers */}
        <Controller
          name="passengers"
          control={control}
          render={({ field }) => (
            <input
              type="number"
              {...field}
              min={1}
              max={9}
              className="w-full border rounded p-2"
              aria-label="Number of passengers"
            />
          )}
        />
        {errors.passengers && (
          <p className="text-red-600 text-sm">{errors.passengers.message}</p>
        )}

        {/* Cabin class */}
        <Controller
          name="cabinClass"
          control={control}
          render={({ field }) => (
            <select {...field} className="w-full border rounded p-2" aria-label="Cabin class">
              <option value="economy">Economy</option>
              <option value="premium_economy">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First</option>
            </select>
          )}
        />
        {errors.cabinClass && (
          <p className="text-red-600 text-sm">{errors.cabinClass.message}</p>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={isSubmitting || mutation.isLoading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          {mutation.isLoading ? 'Searching...' : 'Search Flights'}
        </button>
        {errorMessage && <p className="text-red-600 mt-2">{errorMessage}</p>}
      </form>
    </section>
  );
}
