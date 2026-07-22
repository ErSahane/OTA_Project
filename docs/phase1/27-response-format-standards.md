# Response Format Standards

## Objectives
Provide consistent API and application responses across services.

## Standard Response Shape
```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "requestId": "string",
    "timestamp": "iso8601"
  }
}
```

## Rules
- Use consistent field names and casing.
- Return explicit success or failure state.
- Include pagination metadata when returning lists.
- Avoid leaking sensitive fields in error payloads.

## API Consistency
- All services should follow the same response envelope.
- Web and mobile clients should receive the same contract semantics.
