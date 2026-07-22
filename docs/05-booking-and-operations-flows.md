# Booking and Operations Flows

## 1. Booking Flow
1. Customer searches flights.
2. System retrieves supplier results and applies business rules.
3. Customer selects itinerary and fare.
4. Customer enters passenger and contact details.
5. System validates availability and fare rules.
6. Customer proceeds to payment.
7. Payment service confirms settlement.
8. Booking record is created and confirmation is issued.

## 2. Cancellation Flow
1. Customer or support agent requests cancellation.
2. System checks fare rules and supplier eligibility.
3. If eligible, cancellation is initiated.
4. Refund or credit is calculated according to policy.
5. Cancellation status is updated and communicated.

## 3. Refund Flow
1. Refund request is triggered after cancellation or payment failure.
2. System verifies transaction state and policy eligibility.
3. Refund is processed through the payment gateway.
4. Refund status is updated and a notification is sent.
5. Admin monitors pending and completed refund cases.

## 4. Admin Workflow
1. Admin reviews booking exceptions.
2. Admin verifies payment or supplier response issues.
3. Admin applies manual resolution or escalates to support.
4. Admin records action and closes the workflow.
