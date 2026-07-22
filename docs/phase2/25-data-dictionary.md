# Data Dictionary

## Core Tables and Fields

### customers
- id: primary identifier
- user_id: reference to the owning user
- customer_code: business identifier
- full_name: customer display name
- email: contact email
- phone: contact phone
- created_at: creation timestamp
- updated_at: update timestamp
- deleted_at: logical deletion timestamp
- is_deleted: logical deletion flag

### bookings
- id: primary identifier
- booking_uuid: external booking identifier
- customer_id: reference to customer
- corporate_account_id: optional corporate reference
- status_code: booking lifecycle status
- booking_amount: total booking value
- currency_code: currency of booking
- created_at: creation timestamp
- updated_at: update timestamp
- deleted_at: logical deletion timestamp
- is_deleted: logical deletion flag

### booking_items
- id: primary identifier
- booking_id: reference to booking
- supplier_product_id: reference to supplier inventory item
- fare_rule_id: reference to pricing rule
- segment_type: type of itinerary item
- status_code: status of the item
- created_at: creation timestamp
- updated_at: update timestamp

### payments
- id: primary identifier
- booking_id: reference to booking
- payment_reference: external payment identifier
- amount: payment amount
- currency_code: payment currency
- status_code: payment status
- created_at: creation timestamp
- updated_at: update timestamp

### refunds
- id: primary identifier
- booking_id: reference to booking
- payment_id: reference to payment
- refund_reference: external refund identifier
- amount: refund amount
- status_code: refund status
- created_at: creation timestamp
- updated_at: update timestamp

### support_tickets
- id: primary identifier
- booking_id: optional booking reference
- subject: ticket subject
- status_code: support status
- created_at: creation timestamp
- updated_at: update timestamp

### audit_events
- id: primary identifier
- entity_type: affected domain entity
- entity_id: affected entity identifier
- event_type: event classification
- actor_id: acting user or service id
- created_at: event timestamp
