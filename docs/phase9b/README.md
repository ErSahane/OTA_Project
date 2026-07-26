# Phase 9B - PNR & Ticketing Engine

The PNR & Ticketing Engine introduces GDS-agnostic PNR management, idempotent e-ticket issuance, reissue/void operations, invoice calculation, itinerary segments layout, e-ticket HTML receipt generation, and event-driven signals.

## Core Capabilities

1. **Internal Booking Reference**: Generates unique, uppercase, 6-character internal references starting with `AV` (e.g., `AV4Y8B`) for PNR Records.
2. **Provider PNR Management**: Manages mappings between the platform's internal booking/PNR structures and the provider GDS PNR references.
3. **PNR Synchronization**: Synchronizes segments, classes of service, and flight states from GDS and updates the local state.
4. **Idempotent E-ticket Issuance**: Lock-protected issuance that guarantees identical tickets are returned for duplicate requests.
5. **GDS-Compliant Ticket Numbering**: Generates realistic 13-digit ticket numbers (prefixed with GDS/Airline code e.g. `176`).
6. **Ticket Status Tracking**: Manages lifecycle statuses (`Pending`, `Issued`, `Voided`, `Reissued`, `Failed`) along with coupon validation states.
7. **Ticket Void Support**: Contacts the GDS to void segments and updates coupon and ticket records.
8. **Ticket Reissue Framework**: Handles coupon exchange and reissue, referencing the original parent ticket.
9. **Itinerary & Invoice Builders**: Packages flight segment information and calculates base fares, taxes, and grand totals automatically.
10. **E-ticket HTML PDF Mockup**: Renders clean, styled print/view receipts containing segments, totals, and passenger data.
11. **Event Publishing**: Publishes events via Django signals on Sync, Issuance, Void, and Reissue actions.
12. **Audit trails**: Comprehensive logs tracked in `TicketAuditEvent`.

## API Endpoints

### PNR Management
- `GET /api/v1/ticketing/pnr/{internal_reference}/` - Get details of a PNR Record.
- `POST /api/v1/ticketing/pnr/{internal_reference}/sync/` - Request synchronization of PNR data from the GDS provider.

### Ticket Management
- `GET /api/v1/ticketing/tickets/` - List all tickets owned by the authenticated traveler.
- `GET /api/v1/ticketing/tickets/{id}/` - Retrieve details of a specific ticket.
- `POST /api/v1/ticketing/tickets/issue/` - Idempotently issue tickets for a confirmed booking.
- `POST /api/v1/ticketing/tickets/{id}/void/` - Void an active e-ticket.
- `POST /api/v1/ticketing/tickets/{id}/reissue/` - Reissue an active e-ticket with new pricing/flight data.
- `GET /api/v1/ticketing/tickets/{id}/pdf/` - Stream e-ticket receipt HTML layout.
