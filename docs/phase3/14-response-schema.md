# Response Schema

## Standard Success Envelope
```json
{
  "success": true,
  "data": {},
  "meta": {
    "requestId": "string",
    "timestamp": "2026-07-22T00:00:00Z"
  },
  "error": null
}
```

## Standard List Envelope
```json
{
  "success": true,
  "data": [
    {}
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "hasNext": true
  },
  "error": null
}
```

## Rules
- Use consistent envelope structure across services.
- Include requestId for tracing.
- Keep error payloads explicit and machine-readable.
