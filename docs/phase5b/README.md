# Phase 5B – Identity & Access Management

## Overview
This phase introduces a production-oriented IAM foundation for the OTA platform with a custom user model, JWT-based authentication, role-based access control, password recovery, and account verification flows.

## Implemented capabilities
- Custom user model with email-based authentication and role support
- User profile model
- JWT login, logout, and refresh token support
- Registration, forgot-password, and password-reset flows
- Email verification and OTP framework scaffolding
- RBAC and permission classes for admin/staff checks
- Login rate limiting via local in-memory cache
- Audit logging for security-relevant actions
- Swagger/OpenAPI integration through the API schema routes
- Unit tests covering registration, login, refresh, and password reset

## Verification
- Test command: python manage.py test accounts
- Result: 5 tests passed

## Notes
- The local development setup uses an in-memory cache by default for testability.
- Production deployments should configure Redis and a strong JWT secret.
