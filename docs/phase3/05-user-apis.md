# User APIs

## Endpoints
### Get Current User
- GET /api/v1/users/me

### Update Profile
- PUT /api/v1/users/me

### Change Password
- POST /api/v1/users/me/password

### Preferences
- GET /api/v1/users/me/preferences
- PUT /api/v1/users/me/preferences

## Notes
- User profile APIs should be scoped to the authenticated identity.
- Admin or support portals may use separate administrative endpoints.
