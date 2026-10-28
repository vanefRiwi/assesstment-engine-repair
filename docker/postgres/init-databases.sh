#!/bin/sh
# Runs once, on the first start of an empty PostgreSQL volume.
# Creates one database and one login role per service; each role can only use its own database.
set -eu

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
  -v auth_password="$AUTH_DB_PASSWORD" \
  -v business_password="$BUSINESS_DB_PASSWORD" <<'SQL'
CREATE ROLE auth_user LOGIN PASSWORD :'auth_password';
CREATE ROLE business_user LOGIN PASSWORD :'business_password';

CREATE DATABASE auth_db OWNER auth_user;
CREATE DATABASE business_db OWNER business_user;

-- No cross-service access: only the owner may connect to each database.
REVOKE CONNECT ON DATABASE auth_db FROM PUBLIC;
REVOKE CONNECT ON DATABASE business_db FROM PUBLIC;
GRANT CONNECT ON DATABASE auth_db TO auth_user;
GRANT CONNECT ON DATABASE business_db TO business_user;
SQL
