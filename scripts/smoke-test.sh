#!/usr/bin/env bash
# End-to-end check against a running stack (docker compose up):
# login on auth-service, then use the token on business-service through a full repair flow.
set -euo pipefail

AUTH_URL="${AUTH_URL:-http://localhost:3001/api/v1}"
BUSINESS_URL="${BUSINESS_URL:-http://localhost:8000/api/v1}"
EMAIL="${BOOTSTRAP_ADMIN_EMAIL:-admin@example.com}"
PASSWORD="${BOOTSTRAP_ADMIN_PASSWORD:-ChangeMe-Admin-2026}"
SUFFIX="$(date +%s)"

json() { python3 -c "import json,sys; print(json.load(sys.stdin)$1)"; }
step() { printf '\n==> %s\n' "$1"; }

step "Business API rejects requests without a token"
status=$(curl -s -o /dev/null -w '%{http_code}' "$BUSINESS_URL/clients")
[ "$status" = "401" ] || { echo "expected 401, got $status"; exit 1; }

step "Login on auth-service"
TOKEN=$(curl -sf -X POST "$AUTH_URL/auth/login" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}" | json "['access_token']")
AUTH=(-H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json')

step "Tampered token is rejected by business-service"
status=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${TOKEN}x" "$BUSINESS_URL/clients")
[ "$status" = "401" ] || { echo "expected 401, got $status"; exit 1; }

step "Create client, engine and repair order"
CLIENT_ID=$(curl -sf "${AUTH[@]}" -X POST "$BUSINESS_URL/clients" \
  -d "{\"name\":\"Smoke Mining\",\"document_type\":\"NIT\",\"document_number\":\"SMK$SUFFIX\"}" | json "['id']")
ENGINE_ID=$(curl -sf "${AUTH[@]}" -X POST "$BUSINESS_URL/engines" \
  -d "{\"serial_number\":\"SMK-$SUFFIX\",\"manufacturer\":\"Caterpillar\",\"model\":\"3516B\",\"engine_type\":\"Diesel\",\"client_id\":\"$CLIENT_ID\"}" | json "['id']")
ORDER_ID=$(curl -sf "${AUTH[@]}" -X POST "$BUSINESS_URL/repair-orders" \
  -d "{\"engine_id\":\"$ENGINE_ID\",\"received_at\":\"2026-10-27T14:30:00Z\",\"reported_problem\":\"Smoke test\"}" | json "['id']")

step "Walk the order through its lifecycle"
for status in IN_DIAGNOSIS AWAITING_APPROVAL; do
  curl -sf "${AUTH[@]}" -X PATCH "$BUSINESS_URL/repair-orders/$ORDER_ID/status" -d "{\"status\":\"$status\"}" >/dev/null
done
curl -sf "${AUTH[@]}" -X PATCH "$BUSINESS_URL/repair-orders/$ORDER_ID/approval" -d '{"decision":"APPROVED"}' >/dev/null
for status in IN_REPAIR IN_TESTING COMPLETED DELIVERED; do
  curl -sf "${AUTH[@]}" -X PATCH "$BUSINESS_URL/repair-orders/$ORDER_ID/status" -d "{\"status\":\"$status\"}" >/dev/null
done

step "History has every transition"
COUNT=$(curl -sf "${AUTH[@]}" "$BUSINESS_URL/repair-orders/$ORDER_ID/history" | json ".__len__()")
[ "$COUNT" = "7" ] || { echo "expected 7 history rows, got $COUNT"; exit 1; }

echo
echo "Smoke test passed."
