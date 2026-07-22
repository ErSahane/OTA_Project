# Pagination

## Standard Query Parameters
- page: page number, default 1
- pageSize: number of results, default 20
- limit: optional alias for pageSize

## Response Metadata
- total
- page
- pageSize
- hasNext
- hasPrevious

## Rules
- Default to paginated list responses.
- Support maximum page size caps.
- Include stable ordering for predictable results.
