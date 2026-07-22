# Error Schema

## Standard Error Envelope
```json
{
  "success": false,
  "data": null,
  "meta": {
    "requestId": "string",
    "timestamp": "2026-07-22T00:00:00Z"
  },
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid.",
    "details": [
      {
        "field": "email",
        "message": "Email is required."
      }
    ]
  }
}
```

## Standard Error Codes
- VALIDATION_ERROR
- AUTHENTICATION_FAILED
- AUTHORIZATION_DENIED
- NOT_FOUND
- RATE_LIMITED
- PAYMENT_FAILED
- SUPPLIER_ERROR
- INTERNAL_SERVER_ERROR
