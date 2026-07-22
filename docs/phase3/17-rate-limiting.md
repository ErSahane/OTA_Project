# Rate Limiting

## Objectives
Protect APIs from abuse and maintain service availability.

## Recommended Limits
- Anonymous requests: low threshold per IP
- Authenticated users: moderate threshold per account
- Admin and support endpoints: stricter thresholds
- Search endpoints: burst-capable but protected by quotas

## Strategies
- Token bucket or leaky bucket algorithms
- Per-user and per-IP rate limiting
- Separate limits for write-heavy endpoints
- Return standard 429 responses with retry guidance
