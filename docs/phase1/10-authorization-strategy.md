# Authorization Strategy

## Objectives
Ensure that each actor can access only the resources and actions appropriate to their role and context.

## Recommended Model
- Role-based access control for core platform roles
- Policy-based access for complex workflows
- Attribute-based access control for corporate and agent-specific rules
- Fine-grained permissions for admin and support operations

## Roles
- Customer
- Agent
- Corporate Manager
- Support Agent
- Admin
- Platform Operator

## Enforcement Points
- API layer
- Portal and route-level guards
- Service-level authorization checks
- Data access controls for sensitive records

## Governance
- Access reviews on a scheduled basis
- Separation of duties for finance-related functions
- Approval workflows for privileged operations
