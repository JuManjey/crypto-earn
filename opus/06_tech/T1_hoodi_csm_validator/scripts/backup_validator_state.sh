#!/usr/bin/env bash
# Резервная копия состояния VC: экспорт slashing protection (EIP-3076) + конфигурация.
# Каталог VC содержит keystore и, возможно, пароли в validator_definitions.yml, поэтому
# архив шифруется утилитой age на публичный ключ получателя (секрет на диск не пишется).
# Экспорт slashing protection требует остановленного VC: скрипт останавливает его и запускает снова.
# Использование: AGE_RECIPIENT=age1... scripts/backup_validator_state.sh
set -euo pipefail
cd "$(dirname "$0")/.."

: "${AGE_RECIPIENT:?укажите публичный ключ age: AGE_RECIPIENT=age1...}"
command -v age >/dev/null || { echo "Установите age: https://github.com/FiloSottile/age" >&2; exit 1; }
if (( EUID != 0 )); then
  echo "Файлы VC создаются контейнером от root. Запустите: sudo AGE_RECIPIENT=$AGE_RECIPIENT $0" >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="backups/vc-state-$STAMP.tar.age"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
umask 077

was_running=0
if docker ps --format '{{.Names}}' | grep -qx hoodi-lighthouse-vc; then
  was_running=1
  echo "Останавливаю VC для согласованного экспорта..."
  docker compose --profile validator stop validator
fi

docker compose run --rm --no-deps validator \
  lighthouse --network hoodi account validator slashing-protection export \
  "/root/.lighthouse/hoodi/slashing-protection-export-$STAMP.json"

if (( was_running )); then
  docker compose --profile validator start validator
  echo "VC снова запущен."
fi

mv "data/lighthouse-vc/hoodi/slashing-protection-export-$STAMP.json" "$WORK/"
cp docker-compose.yml "$WORK/"
[[ -f .env ]] && cp .env "$WORK/"
tar -C data -cf "$WORK/lighthouse-vc.tar" lighthouse-vc
tar -C "$WORK" -cf - . | age -r "$AGE_RECIPIENT" -o "$OUT"
echo "Готово: $OUT ($(du -h "$OUT" | cut -f1)). Храните копию вне этого сервера."
echo "Восстановление на новом хосте: старый VC остановлен >= 2 эпох, импорт slashing protection, затем запуск с doppelganger protection."
