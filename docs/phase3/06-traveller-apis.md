# Traveller APIs

## Endpoints
### Create Traveller
- POST /api/v1/travelers

### List Travelers
- GET /api/v1/travelers

### Get Traveller
- GET /api/v1/travelers/{travellerId}

### Update Traveller
- PUT /api/v1/travelers/{travellerId}

### Delete Traveller
- DELETE /api/v1/travelers/{travellerId}

## Notes
- Traveller records are associated with bookings and should be validated against booking context.
- PII should be handled according to security and compliance requirements.
