# OpenAPI Specification Structure

## Recommended Structure
- info
- servers
- securitySchemes
- tags
- paths
- components
  - schemas
  - parameters
  - responses
  - examples
  - securitySchemes

## Suggested Top-Level Sections
```yaml
openapi: 3.1.0
info:
  title: AstraVoyage OTA API
  version: 1.0.0
  description: Enterprise API contract for OTA platform services.
servers:
  - url: https://api.astrovoyage.example.com
paths: {}
components:
  schemas: {}
  securitySchemes: {}
```

## Notes
- Separate schemas for request and response payloads.
- Keep examples realistic and business-focused.
- Describe security requirements at both service and operation levels.
