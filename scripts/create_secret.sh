#!/usr/bin/env bash
set -e
SECRET_B64=${1:-"cGFzc3dvcmQxMjM="}
curl -s -X POST http://localhost:8000/vault/secret/create/ \
  -H "Content-Type: application/json" \
  -d "{\"secret\":\"${SECRET_B64}\"}"