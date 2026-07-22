# Logging Strategy

## Goals
Create a consistent, secure, and actionable log model across all services and applications.

## Logging Principles
- Structured logging for machine-readable analysis
- Correlation IDs for end-to-end tracing
- Sensitive data redaction
- Log levels mapped to severity
- Centralized log aggregation

## Recommended Log Categories
- Application logs
- Security and authentication logs
- Payment and booking workflow logs
- Integration and supplier logs
- Audit logs for critical operations

## Retention Guidance
- Operational logs retained for a defined period with tiered storage
- Audit logs retained longer to support compliance review
- Archive older logs to low-cost storage
