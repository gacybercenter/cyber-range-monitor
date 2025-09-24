# API Design Docs





## Authentication

- OAuth2 with JWT tokens
- Store the Roles enum in the token
- Have a "credential_version" or `cver` cached in redis
to prevent stale tokens
- On login, synchronize the cver from the DB in redis
- `SETEX` the encoded msgspec refresh claim for `refresh_ttl`
