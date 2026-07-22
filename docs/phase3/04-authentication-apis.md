# Authentication APIs

## Endpoints
### Register
- POST /api/v1/auth/register

### Login
- POST /api/v1/auth/login

### Refresh Token
- POST /api/v1/auth/refresh

### Logout
- POST /api/v1/auth/logout

### Forgot Password
- POST /api/v1/auth/password/forgot

### Reset Password
- POST /api/v1/auth/password/reset

## Authentication Principles
- Use OAuth 2.0 / OpenID Connect patterns.
- Return short-lived access tokens and refresh tokens.
- Enforce MFA for privileged roles.
- Support token revocation for logout and compromise detection.
