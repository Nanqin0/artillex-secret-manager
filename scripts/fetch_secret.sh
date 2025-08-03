#!/usr/bin/env bash
set -e
SID="$1"
[ -z "$SID" ] && { echo "Usage: $0 <secret_id>"; exit 1; }
curl -s -X POST http://localhost:8000/vault/secret/fetch \
  -H "Content-Type: application/json" \
  -d "{\"secret_id\":\"${SID}\"}"
