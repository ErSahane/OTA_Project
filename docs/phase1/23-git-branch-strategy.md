# Git Branch Strategy

## Branch Model
- main: production-ready code
- develop: integration branch for ongoing work
- feature/*: short-lived branches for new work
- hotfix/*: emergency production fixes
- release/*: release preparation branches

## Branch Rules
- Protect main from direct pushes.
- Merge to develop only after validation.
- Use feature branches for isolated work.
- Maintain branch hygiene by deleting merged branches.

## Merge Policy
- Pull requests must be approved.
- CI checks must pass before merge.
- Merges should be fast-forward where feasible.
