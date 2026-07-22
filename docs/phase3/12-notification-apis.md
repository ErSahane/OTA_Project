# Notification APIs

## Endpoints
### Send Notification
- POST /api/v1/notifications

### Get Notification
- GET /api/v1/notifications/{notificationId}

### List Notifications
- GET /api/v1/notifications

## Notes
- Notifications should be asynchronous where possible.
- Notification payloads should include correlation identifiers and delivery status metadata.
