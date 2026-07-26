"use client";

import React, { useState } from 'react';
import PassengerForm from './components/PassengerForm';
import ContactForm from './components/ContactForm';
import BookingSummary from './components/BookingSummary';
import ReviewConfirm from './components/ReviewConfirm';
import { useBooking } from './BookingContext';
import { useRouter } from 'next/navigation';

export default function BookingPage() {
  const [step, setStep] = useState(1);
  const { data } = useBooking();
  const router = useRouter();

  const goNext = () => setStep((s) => s + 1);
  const goBack = () => setStep((s) => Math.max(s - 1, 1));

  // After review, proceed to payment
  const handleProceedToPayment = () => {
    router.push('/booking/payment');
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      {step === 1 && <PassengerForm onNext={goNext} />}
      {step === 2 && <ContactForm onNext={goNext} />}
      {step === 3 && (
        <BookingSummary onNext={goNext} onBack={goBack} />
      )}
      {step === 4 && (
        <ReviewConfirm
          data={data}
          onBack={goBack}
          onConfirm={handleProceedToPayment}
        />
      )}
    </div>
  );
}
