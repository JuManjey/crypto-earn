#!/usr/bin/env bash
# Генерирует общий JWT-секрет для Engine API (EL <-> CL). Не перезаписывает существующий.
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
mkdir -p secrets
if [[ -s secrets/jwt.hex ]]; then
  echo "secrets/jwt.hex уже существует — оставляю как есть."
  exit 0
fi
openssl rand -hex 32 | tr -d '\n' > secrets/jwt.hex
chmod 600 secrets/jwt.hex
echo "Создан secrets/jwt.hex (64 hex-символа, права 600). Не коммитьте каталог secrets/."
