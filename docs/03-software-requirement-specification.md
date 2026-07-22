# Software Requirement Specification (SRS)

## 1. Product Overview
AstraVoyage is a web-first OTA platform with future support for mobile and portal-based experiences.

## 2. Functional Requirements
### FR1: User Registration and Authentication
The system shall allow users to register, sign in, and manage profile data securely.

### FR2: Flight Search
The system shall allow users to search for flights by origin, destination, travel date, cabin class, passenger count, and trip type.

### FR3: Fare Display
The system shall present fare options with pricing breakdown, baggage rules, and change/cancellation information where available.

### FR4: Booking Creation
The system shall allow users to create bookings with traveler details and fare selection.

### FR5: Payment Processing
The system shall support secure payment initiation and confirmation for flight bookings.

### FR6: Booking Management
The system shall allow users and admins to track booking status, view details, and manage support actions.

### FR7: Cancellation and Refund
The system shall support cancellation requests and refund workflows based on supplier and policy rules.

### FR8: Admin Operations
Admin users shall be able to review bookings, manage support issues, and monitor platform activity.

## 3. Non-Functional Requirements
- Availability: 99.9% target for production services.
- Performance: search and booking APIs should respond within acceptable thresholds under peak load.
- Security: role-based access, encryption, audit logging, and secure payment handling.
- Scalability: architecture must support horizontal scaling for traffic growth.
- Reliability: service degradation handling and retry logic for supplier integrations.
- Maintainability: modular services and documented interfaces.

## 4. Constraints
- MVP scope is limited to flight bookings.
- Implementation must follow phased delivery with clear milestone gates.
- Supplier integrations must be abstracted to protect business logic from third-party changes.
